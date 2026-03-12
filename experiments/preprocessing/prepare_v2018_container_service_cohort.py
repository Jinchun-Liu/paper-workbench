#!/usr/bin/env python3
"""Build a service-level cohort from Alibaba v2018 container traces."""

from __future__ import annotations

import argparse
from collections import defaultdict
import re
import subprocess
import tarfile
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd


META_COLUMNS = [
    "container_id",
    "machine_id",
    "time_stamp",
    "app_du",
    "status",
    "cpu_request",
    "cpu_limit",
    "mem_size",
]

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


def container_numeric_id(container_id: str) -> int | None:
    match = re.match(r"c_(\d+)$", str(container_id))
    if match is None:
        return None
    return int(match.group(1))


def open_tar_stream(source: str):
    parsed = urllib.parse.urlparse(source)
    if parsed.scheme in {"http", "https"}:
        response = urllib.request.urlopen(source, timeout=120)
        tar = tarfile.open(fileobj=response, mode="r|gz")
        return response, tar
    tar = tarfile.open(Path(source), mode="r:gz")
    return None, tar


def validate_local_usage_archive(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Local usage archive does not exist: {path}")

    result = subprocess.run(
        ["gzip", "-t", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise OSError(f"gzip integrity check failed for {path}: {detail or 'unknown error'}")

    with tarfile.open(path, "r:gz") as tar:
        member = next((m for m in tar.getmembers() if m.isfile() and m.name.endswith(".csv")), None)
        if member is None:
            raise FileNotFoundError(f"No CSV member found in local usage archive: {path}")


def read_container_meta(meta_tar: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    with tarfile.open(meta_tar, "r:gz") as tar:
        member = next(m for m in tar.getmembers() if m.isfile() and m.name.endswith(".csv"))
        stream = tar.extractfile(member)
        if stream is None:
            raise FileNotFoundError(f"Could not extract CSV from {meta_tar}")
        meta = pd.read_csv(stream, header=None, names=META_COLUMNS)

    meta["time_stamp"] = pd.to_numeric(meta["time_stamp"], errors="coerce")
    meta["cpu_request"] = pd.to_numeric(meta["cpu_request"], errors="coerce")
    meta["mem_size"] = pd.to_numeric(meta["mem_size"], errors="coerce")
    meta = meta.dropna(subset=["container_id", "app_du", "time_stamp", "cpu_request"])
    meta = meta.sort_values(["container_id", "time_stamp"])

    container_info = (
        meta.groupby("container_id")
        .agg(
            app_du=("app_du", "last"),
            cpu_request=("cpu_request", "max"),
            mem_size=("mem_size", "max"),
            min_ts=("time_stamp", "min"),
            max_ts=("time_stamp", "max"),
            event_count=("container_id", "size"),
            machine_count=("machine_id", "nunique"),
        )
        .reset_index()
    )
    container_info["cpu_request_cores"] = container_info["cpu_request"] / 100.0

    app_summary = (
        container_info.groupby("app_du")
        .agg(
            unique_containers=("container_id", "nunique"),
            mean_cpu_request_cores=("cpu_request_cores", "mean"),
            median_cpu_request_cores=("cpu_request_cores", "median"),
            mean_mem_size=("mem_size", "mean"),
            min_ts=("min_ts", "min"),
            max_ts=("max_ts", "max"),
            container_events=("event_count", "sum"),
            machines=("machine_count", "sum"),
        )
        .reset_index()
    )
    app_summary["span_seconds"] = app_summary["max_ts"] - app_summary["min_ts"]
    return container_info, app_summary.sort_values(["unique_containers", "span_seconds"], ascending=False)


def select_apps(app_summary: pd.DataFrame, top_n: int, min_span_seconds: int) -> list[str]:
    eligible = app_summary[app_summary["span_seconds"] >= min_span_seconds].copy()
    if eligible.empty:
        raise ValueError("No app_du passes the minimum span threshold.")
    return eligible.head(top_n)["app_du"].tolist()


def stream_usage_matches(
    usage_source: str,
    selected_info: pd.DataFrame,
    chunk_size: int,
    temp_csv: Path,
    max_container_id: int | None = None,
) -> tuple[int, int, int | None]:
    temp_csv.parent.mkdir(parents=True, exist_ok=True)
    if temp_csv.exists():
        temp_csv.unlink()

    app_map = selected_info.set_index("container_id")["app_du"].to_dict()
    cpu_map = selected_info.set_index("container_id")["cpu_request_cores"].to_dict()
    mem_map = selected_info.set_index("container_id")["mem_size"].to_dict()
    selected_ids = set(app_map)

    response = None
    tar = None
    rows_scanned = 0
    rows_matched = 0
    max_seen_container_id: int | None = None
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
            usecols=["container_id", "time_stamp", "cpu_util_percent", "mem_util_percent"],
            chunksize=chunk_size,
            dtype={"container_id": "string"},
            low_memory=False,
        )
        first_write = True
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
            rows_scanned += len(chunk)
            max_seen_container_id = int(chunk["numeric_id"].max())

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

            view = chunk[chunk["container_id"].isin(selected_ids)].copy()
            if view.empty:
                if stop_after_chunk:
                    break
                continue
            view["time_stamp"] = pd.to_numeric(view["time_stamp"], errors="coerce")
            view["cpu_util_percent"] = pd.to_numeric(view["cpu_util_percent"], errors="coerce")
            view["mem_util_percent"] = pd.to_numeric(view["mem_util_percent"], errors="coerce")
            view = view.dropna(subset=["time_stamp", "cpu_util_percent", "mem_util_percent"])
            if view.empty:
                if stop_after_chunk:
                    break
                continue
            view["minute_index"] = (view["time_stamp"].astype("int64") // 60).astype("int64")
            view["app_du"] = view["container_id"].map(app_map)
            view["cpu_request_cores"] = view["container_id"].map(cpu_map)
            view["mem_size"] = view["container_id"].map(mem_map)
            view["cpu_used_cores_proxy"] = view["cpu_request_cores"] * view["cpu_util_percent"] / 100.0
            grouped = (
                view.groupby(["container_id", "app_du", "minute_index"], as_index=False)
                .agg(
                    cpu_util_mean=("cpu_util_percent", "mean"),
                    mem_util_mean=("mem_util_percent", "mean"),
                    cpu_used_cores_proxy=("cpu_used_cores_proxy", "mean"),
                    cpu_request_cores=("cpu_request_cores", "max"),
                    mem_size=("mem_size", "max"),
                    sample_count=("container_id", "size"),
                )
            )
            rows_matched += len(grouped)
            grouped.to_csv(temp_csv, mode="a", header=first_write, index=False)
            first_write = False

            if stop_after_chunk:
                break
    finally:
        if tar is not None:
            tar.close()
        if response is not None:
            response.close()

    if not temp_csv.exists():
        raise ValueError("No matching container usage rows were extracted for the selected apps.")
    return rows_scanned, rows_matched, max_seen_container_id


def build_service_cohort(
    filtered_csv: Path,
    selected_info: pd.DataFrame,
    selected_apps: set[str] | None = None,
    chunk_size: int = 1_000_000,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    service_accumulator: dict[tuple[str, int], dict[str, float]] = {}
    matched_containers_by_app: dict[str, set[str]] = defaultdict(set)
    chunk_iter = pd.read_csv(filtered_csv, chunksize=chunk_size)
    for chunk in chunk_iter:
        if selected_apps is not None:
            chunk = chunk[chunk["app_du"].isin(selected_apps)]
        if chunk.empty:
            continue
        for app_du, container_ids in chunk.groupby("app_du")["container_id"]:
            matched_containers_by_app[str(app_du)].update(container_ids.astype(str).unique().tolist())
        grouped = (
            chunk.groupby(["app_du", "minute_index"], as_index=False)
            .agg(
                active_container_count=("container_id", "count"),
                cpu_util_sum=("cpu_util_mean", "sum"),
                mem_util_sum=("mem_util_mean", "sum"),
                service_cpu_used_cores_proxy=("cpu_used_cores_proxy", "sum"),
                service_cpu_request_cores_total=("cpu_request_cores", "sum"),
                mem_size_sum=("mem_size", "sum"),
                service_sample_count=("sample_count", "sum"),
            )
        )
        for row in grouped.itertuples(index=False):
            key = (str(row.app_du), int(row.minute_index))
            slot = service_accumulator.setdefault(
                key,
                {
                    "active_container_count": 0.0,
                    "cpu_util_sum": 0.0,
                    "mem_util_sum": 0.0,
                    "service_cpu_used_cores_proxy": 0.0,
                    "service_cpu_request_cores_total": 0.0,
                    "mem_size_sum": 0.0,
                    "service_sample_count": 0.0,
                },
            )
            slot["active_container_count"] += float(row.active_container_count)
            slot["cpu_util_sum"] += float(row.cpu_util_sum)
            slot["mem_util_sum"] += float(row.mem_util_sum)
            slot["service_cpu_used_cores_proxy"] += float(row.service_cpu_used_cores_proxy)
            slot["service_cpu_request_cores_total"] += float(row.service_cpu_request_cores_total)
            slot["mem_size_sum"] += float(row.mem_size_sum)
            slot["service_sample_count"] += float(row.service_sample_count)

    service_rows: list[dict] = []
    for (app_du, minute_index), values in service_accumulator.items():
        count = max(values["active_container_count"], 1.0)
        service_rows.append(
            {
                "app_du": app_du,
                "minute_index": minute_index,
                "active_container_count": values["active_container_count"],
                "service_cpu_utilization_mean": values["cpu_util_sum"] / count,
                "service_memory_utilization_mean": values["mem_util_sum"] / count,
                "service_cpu_used_cores_proxy": values["service_cpu_used_cores_proxy"],
                "service_cpu_request_cores_total": values["service_cpu_request_cores_total"],
                "mean_container_mem_size": values["mem_size_sum"] / count,
                "service_sample_count": int(values["service_sample_count"]),
            }
        )
    service = pd.DataFrame(service_rows).sort_values(["app_du", "minute_index"])
    service["service_cpu_utilization_weighted"] = np.where(
        service["service_cpu_request_cores_total"] > 1e-9,
        100.0 * service["service_cpu_used_cores_proxy"] / service["service_cpu_request_cores_total"],
        np.nan,
    )

    global_start = int(service["minute_index"].min())
    global_end = int(service["minute_index"].max())
    full_index = pd.Index(range(global_start, global_end + 1), name="minute_index")
    span = len(full_index)

    request_lookup = (
        selected_info.groupby("app_du")
        .agg(
            selected_containers=("container_id", "nunique"),
            mean_container_request_cores=("cpu_request_cores", "mean"),
            median_container_request_cores=("cpu_request_cores", "median"),
            mean_container_mem_size=("mem_size", "mean"),
            min_selected_ts=("min_ts", "min"),
            max_selected_ts=("max_ts", "max"),
        )
        .reset_index()
    )
    request_lookup["unique_containers"] = request_lookup["selected_containers"].astype(int)
    request_lookup["span_seconds"] = (
        request_lookup["max_selected_ts"] - request_lookup["min_selected_ts"]
    ).astype(int)
    matched_lookup = pd.DataFrame(
        [
            {"app_du": app_du, "matched_containers": len(container_ids)}
            for app_du, container_ids in matched_containers_by_app.items()
        ]
    )

    filled_parts: list[pd.DataFrame] = []
    summary_rows: list[dict] = []
    for app_du, group in service.groupby("app_du"):
        entity = group.set_index("minute_index").sort_index()
        entity = entity.reindex(full_index)
        missing_mask = entity["service_cpu_used_cores_proxy"].isna()

        for col in [
            "service_cpu_utilization_mean",
            "service_memory_utilization_mean",
            "service_cpu_used_cores_proxy",
            "service_cpu_request_cores_total",
            "service_cpu_utilization_weighted",
            "mean_container_mem_size",
        ]:
            entity[col] = entity[col].interpolate(limit_direction="both")

        entity["active_container_count"] = (
            entity["active_container_count"].interpolate(limit_direction="both").round().clip(lower=1)
        )
        entity["service_sample_count"] = entity["service_sample_count"].fillna(0).astype(int)
        entity["imputed"] = missing_mask.astype(int)
        entity["app_du"] = app_du
        filled = entity.reset_index()
        filled_parts.append(filled)

        observed_minutes = int(group["minute_index"].nunique())
        summary_rows.append(
            {
                "app_du": app_du,
                "observed_minutes": observed_minutes,
                "coverage_ratio": observed_minutes / span,
                "imputed_ratio": float(filled["imputed"].mean()),
                "mean_active_container_count": float(filled["active_container_count"].mean()),
                "mean_service_cpu_used_cores_proxy": float(filled["service_cpu_used_cores_proxy"].mean()),
                "peak_service_cpu_used_cores_proxy": float(filled["service_cpu_used_cores_proxy"].max()),
                "global_minute_start": global_start,
                "global_minute_end": global_end,
                "global_span_minutes": span,
            }
        )

    filled_df = pd.concat(filled_parts, ignore_index=True)
    summary_df = (
        pd.DataFrame(summary_rows)
        .merge(request_lookup, on="app_du", how="left")
        .merge(matched_lookup, on="app_du", how="left")
    )
    summary_df["matched_containers"] = summary_df["matched_containers"].fillna(0).astype(int)
    summary_df["unique_containers"] = summary_df["unique_containers"].fillna(0).astype(int)
    summary_df["container_hit_ratio"] = np.where(
        summary_df["unique_containers"] > 0,
        summary_df["matched_containers"] / summary_df["unique_containers"],
        np.nan,
    )
    summary_df = summary_df.drop(columns=["min_selected_ts", "max_selected_ts"])
    return filled_df, summary_df.sort_values("coverage_ratio", ascending=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--meta-tar", type=Path, required=True)
    parser.add_argument("--usage-source", type=str, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--summary-csv", type=Path, required=True)
    parser.add_argument("--selected-apps-csv", type=Path, required=True)
    parser.add_argument("--temp-filtered-csv", type=Path, required=True)
    parser.add_argument("--top-n-apps", type=int, default=5)
    parser.add_argument("--min-span-seconds", type=int, default=650_000)
    parser.add_argument("--chunk-size", type=int, default=400_000)
    parser.add_argument("--max-container-id", type=int, default=None)
    parser.add_argument("--selected-app-du", action="append", default=None)
    parser.add_argument("--selected-apps-file", type=Path, default=None)
    parser.add_argument("--skip-archive-check", action="store_true")
    args = parser.parse_args()

    container_info, app_summary = read_container_meta(args.meta_tar)
    if args.selected_app_du:
        selected_apps = list(dict.fromkeys(args.selected_app_du))
    elif args.selected_apps_file:
        selected_apps = [
            line.strip()
            for line in args.selected_apps_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    else:
        selected_apps = select_apps(app_summary, args.top_n_apps, args.min_span_seconds)
    selected_info = container_info[container_info["app_du"].isin(selected_apps)].copy()
    if selected_info.empty:
        raise ValueError("No container metadata found for the requested app_du selection.")
    app_summary[app_summary["app_du"].isin(selected_apps)].to_csv(args.selected_apps_csv, index=False)

    parsed_usage = urllib.parse.urlparse(args.usage_source)
    if parsed_usage.scheme not in {"http", "https"} and not args.skip_archive_check:
        validate_local_usage_archive(Path(args.usage_source))

    rows_scanned, rows_matched, max_seen_container_id = stream_usage_matches(
        args.usage_source,
        selected_info,
        args.chunk_size,
        args.temp_filtered_csv,
        max_container_id=args.max_container_id,
    )
    cohort_df, summary_df = build_service_cohort(args.temp_filtered_csv, selected_info)
    summary_df["usage_rows_scanned"] = rows_scanned
    summary_df["matched_container_minute_rows"] = rows_matched
    summary_df["max_seen_container_id"] = max_seen_container_id

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    cohort_df.to_csv(args.output_csv, index=False)
    args.summary_csv.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(args.summary_csv, index=False)


if __name__ == "__main__":
    main()
