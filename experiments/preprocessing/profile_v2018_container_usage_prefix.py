#!/usr/bin/env python3
"""Profile app_du coverage within a streamed or full container_usage scan."""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from prepare_v2018_container_service_cohort import (
    container_numeric_id,
    open_tar_stream,
    read_container_meta,
    validate_local_usage_archive,
)

USAGE_COLUMNS = [
    "container_id",
    "machine_id",
    "time_stamp",
    "cpu_util_percent",
    "mem_util_percent",
    "cpi",
    "mem_gps",
    "mpki",
    "net_in",
    "net_out",
    "disk_io_percent",
]


def profile_usage_coverage(
    meta_tar: Path,
    usage_source: str,
    min_span_seconds: int = 650_000,
    min_containers: int = 60,
    max_container_id: int | None = None,
) -> pd.DataFrame:
    container_info, app_summary = read_container_meta(meta_tar)
    eligible_apps = app_summary[
        (app_summary["span_seconds"] >= min_span_seconds)
        & (app_summary["unique_containers"] >= min_containers)
    ].copy()
    eligible_set = set(eligible_apps["app_du"])
    selected_container_info = container_info[container_info["app_du"].isin(eligible_set)].copy()
    app_map = selected_container_info.set_index("container_id")["app_du"].to_dict()
    meta_lookup = eligible_apps.set_index("app_du")
    app_bounds = (
        selected_container_info.assign(
            cid_num=selected_container_info["container_id"].str.extract(r"c_(\d+)").astype(int)
        )
        .groupby("app_du")
        .agg(
            min_container_id_meta=("cid_num", "min"),
            max_container_id_meta=("cid_num", "max"),
        )
    )

    seen_containers: dict[str, set[str]] = defaultdict(set)
    seen_minutes: dict[str, set[int]] = defaultdict(set)
    matched_rows_by_app: dict[str, int] = defaultdict(int)
    min_minute: dict[str, int] = {}
    max_minute: dict[str, int] = {}
    nonblank_rows = 0
    matched_rows = 0
    max_seen_container_id = 0

    response = None
    tar = None
    try:
        response, tar = open_tar_stream(usage_source)
        member = next(m for m in tar if m.isfile() and m.name.endswith(".csv"))
        stream = tar.extractfile(member)
        if stream is None:
            raise FileNotFoundError(f"Could not extract CSV from {usage_source}")

        chunk_iter = pd.read_csv(
            stream,
            header=None,
            names=USAGE_COLUMNS,
            usecols=["container_id", "time_stamp"],
            chunksize=1_000_000,
            dtype={"container_id": "string"},
            low_memory=False,
        )
        for chunk in chunk_iter:
            chunk = chunk.dropna(subset=["container_id"])
            if chunk.empty:
                continue
            chunk["container_id"] = chunk["container_id"].astype("string").str.strip()
            chunk = chunk[chunk["container_id"] != ""]
            if chunk.empty:
                continue

            chunk["numeric_id"] = (
                chunk["container_id"].str.extract(r"c_(\d+)", expand=False).astype("Int64")
            )
            chunk = chunk.dropna(subset=["numeric_id"])
            if chunk.empty:
                continue
            chunk["numeric_id"] = chunk["numeric_id"].astype("int64")
            nonblank_rows += len(chunk)
            max_seen_container_id = max(max_seen_container_id, int(chunk["numeric_id"].max()))

            stop_after_chunk = False
            if max_container_id is not None:
                over_limit = chunk["numeric_id"] > max_container_id
                if over_limit.any():
                    stop_after_chunk = True
                    chunk = chunk.loc[~over_limit].copy()
            if chunk.empty:
                if stop_after_chunk:
                    break
                continue

            chunk["app_du"] = chunk["container_id"].map(app_map)
            view = chunk.dropna(subset=["app_du"]).copy()
            if view.empty:
                if stop_after_chunk:
                    break
                continue
            view["time_stamp"] = pd.to_numeric(view["time_stamp"], errors="coerce")
            view = view.dropna(subset=["time_stamp"])
            if view.empty:
                if stop_after_chunk:
                    break
                continue
            view["minute_index"] = (view["time_stamp"].astype("int64") // 60).astype("int64")
            matched_rows += len(view)

            for app_du, group in view.groupby("app_du"):
                container_values = group["container_id"].dropna().astype(str).unique().tolist()
                minute_values = group["minute_index"].dropna().astype("int64").unique().tolist()
                seen_containers[app_du].update(container_values)
                seen_minutes[app_du].update(minute_values)
                matched_rows_by_app[app_du] += len(group)
                local_min = int(group["minute_index"].min())
                local_max = int(group["minute_index"].max())
                if app_du not in min_minute or local_min < min_minute[app_du]:
                    min_minute[app_du] = local_min
                if app_du not in max_minute or local_max > max_minute[app_du]:
                    max_minute[app_du] = local_max

            if stop_after_chunk:
                break
    finally:
        if tar is not None:
            tar.close()
        if response is not None:
            response.close()

    rows: list[dict] = []
    for app_du in sorted(seen_containers):
        minute_count = len(seen_minutes[app_du])
        span_minutes = max_minute[app_du] - min_minute[app_du] + 1
        total_containers = int(meta_lookup.loc[app_du, "unique_containers"])
        rows.append(
            {
                "app_du": app_du,
                "usage_containers_seen": len(seen_containers[app_du]),
                "meta_unique_containers": total_containers,
                "container_hit_ratio": len(seen_containers[app_du]) / max(total_containers, 1),
                "observed_minutes": minute_count,
                "min_minute": min_minute[app_du],
                "max_minute": max_minute[app_du],
                "span_minutes": span_minutes,
                "minute_coverage_ratio": minute_count / max(span_minutes, 1),
                "matched_rows_for_app": matched_rows_by_app[app_du],
                "meta_span_seconds": int(meta_lookup.loc[app_du, "span_seconds"]),
                "min_container_id_meta": int(app_bounds.loc[app_du, "min_container_id_meta"]),
                "max_container_id_meta": int(app_bounds.loc[app_du, "max_container_id_meta"]),
            }
        )

    profile = pd.DataFrame(rows)
    if not profile.empty:
        profile = profile.sort_values(
            ["container_hit_ratio", "minute_coverage_ratio", "usage_containers_seen"],
            ascending=[False, False, False],
        )
    profile["profile_max_container_id"] = max_seen_container_id
    profile["nonblank_rows_scanned"] = nonblank_rows
    profile["matched_rows_scanned"] = matched_rows
    return profile


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--meta-tar", type=Path, required=True)
    parser.add_argument("--usage-source", type=str, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--max-container-id", type=int, default=None)
    parser.add_argument("--min-span-seconds", type=int, default=650_000)
    parser.add_argument("--min-containers", type=int, default=60)
    parser.add_argument("--skip-archive-check", action="store_true")
    args = parser.parse_args()

    if "://" not in args.usage_source and not args.skip_archive_check:
        validate_local_usage_archive(Path(args.usage_source))

    profile = profile_usage_coverage(
        meta_tar=args.meta_tar,
        usage_source=args.usage_source,
        min_span_seconds=args.min_span_seconds,
        min_containers=args.min_containers,
        max_container_id=args.max_container_id,
    )
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    profile.to_csv(args.output_csv, index=False)


if __name__ == "__main__":
    main()
