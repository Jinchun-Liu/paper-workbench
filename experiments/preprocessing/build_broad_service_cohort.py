#!/usr/bin/env python3
"""Build a broader Alibaba service cohort from a local full container_usage mirror."""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from prepare_v2018_container_service_cohort import (
    build_service_cohort,
    open_tar_stream,
    read_container_meta,
    validate_local_usage_archive,
)
from profile_v2018_container_usage_prefix import USAGE_COLUMNS


def profile_and_extract_single_pass(
    usage_archive: Path,
    selected_info: pd.DataFrame,
    profile_csv: Path,
    filtered_csv: Path,
    chunk_size: int,
) -> tuple[pd.DataFrame, int, int, int]:
    app_map = selected_info.set_index("container_id")["app_du"].to_dict()
    cpu_map = selected_info.set_index("container_id")["cpu_request_cores"].to_dict()
    mem_map = selected_info.set_index("container_id")["mem_size"].to_dict()
    selected_ids = set(app_map)
    meta_lookup = (
        selected_info.groupby("app_du")
        .agg(
            unique_containers=("container_id", "nunique"),
            span_seconds=("max_ts", "max"),
            min_ts=("min_ts", "min"),
        )
        .reset_index()
    )
    meta_lookup["span_seconds"] = meta_lookup["span_seconds"] - meta_lookup["min_ts"]
    meta_lookup = meta_lookup.drop(columns=["min_ts"]).set_index("app_du")
    app_bounds = (
        selected_info.assign(
            cid_num=selected_info["container_id"].str.extract(r"c_(\d+)").astype(int)
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
    rows_scanned = 0
    rows_matched = 0
    max_seen_container_id = 0

    filtered_csv.parent.mkdir(parents=True, exist_ok=True)
    if filtered_csv.exists():
        filtered_csv.unlink()
    first_write = True

    response = None
    tar = None
    try:
        response, tar = open_tar_stream(str(usage_archive))
        member = next(m for m in tar if m.isfile() and m.name.endswith(".csv"))
        stream = tar.extractfile(member)
        if stream is None:
            raise FileNotFoundError(f"Could not extract CSV from {usage_archive}")

        chunk_iter = pd.read_csv(
            stream,
            header=None,
            names=USAGE_COLUMNS,
            usecols=["container_id", "time_stamp", "cpu_util_percent", "mem_util_percent"],
            chunksize=chunk_size,
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
            rows_scanned += len(chunk)
            max_seen_container_id = max(max_seen_container_id, int(chunk["numeric_id"].max()))

            view = chunk[chunk["container_id"].isin(selected_ids)].copy()
            if view.empty:
                continue
            view["app_du"] = view["container_id"].map(app_map)
            view = view.dropna(subset=["app_du"])
            if view.empty:
                continue
            view["time_stamp"] = pd.to_numeric(view["time_stamp"], errors="coerce")
            view["cpu_util_percent"] = pd.to_numeric(view["cpu_util_percent"], errors="coerce")
            view["mem_util_percent"] = pd.to_numeric(view["mem_util_percent"], errors="coerce")
            view = view.dropna(subset=["time_stamp", "cpu_util_percent", "mem_util_percent"])
            if view.empty:
                continue
            view["minute_index"] = (view["time_stamp"].astype("int64") // 60).astype("int64")

            for app_du, group in view.groupby("app_du"):
                seen_containers[app_du].update(group["container_id"].astype(str).unique().tolist())
                minute_values = group["minute_index"].astype("int64").unique().tolist()
                seen_minutes[app_du].update(minute_values)
                matched_rows_by_app[app_du] += len(group)
                local_min = int(group["minute_index"].min())
                local_max = int(group["minute_index"].max())
                if app_du not in min_minute or local_min < min_minute[app_du]:
                    min_minute[app_du] = local_min
                if app_du not in max_minute or local_max > max_minute[app_du]:
                    max_minute[app_du] = local_max

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
            grouped.to_csv(filtered_csv, mode="a", header=first_write, index=False)
            first_write = False
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
                "profile_max_container_id": max_seen_container_id,
                "nonblank_rows_scanned": rows_scanned,
                "matched_rows_scanned": sum(matched_rows_by_app.values()),
            }
        )
    profile_df = pd.DataFrame(rows)
    if not profile_df.empty:
        profile_df = profile_df.sort_values(
            ["container_hit_ratio", "minute_coverage_ratio", "usage_containers_seen"],
            ascending=[False, False, False],
        )
    profile_csv.parent.mkdir(parents=True, exist_ok=True)
    profile_df.to_csv(profile_csv, index=False)
    return profile_df, rows_scanned, rows_matched, max_seen_container_id


def profile_and_build_cohort_single_pass(
    usage_archive: Path,
    selected_info: pd.DataFrame,
    profile_csv: Path,
    chunk_size: int,
) -> tuple[pd.DataFrame, pd.DataFrame, int, int, int]:
    app_map = selected_info.set_index("container_id")["app_du"].to_dict()
    cpu_map = selected_info.set_index("container_id")["cpu_request_cores"].to_dict()
    mem_map = selected_info.set_index("container_id")["mem_size"].to_dict()
    selected_ids = set(app_map)
    meta_lookup = (
        selected_info.groupby("app_du")
        .agg(
            unique_containers=("container_id", "nunique"),
            span_seconds=("max_ts", "max"),
            min_ts=("min_ts", "min"),
        )
        .reset_index()
    )
    meta_lookup["span_seconds"] = meta_lookup["span_seconds"] - meta_lookup["min_ts"]
    meta_lookup = meta_lookup.drop(columns=["min_ts"]).set_index("app_du")
    app_bounds = (
        selected_info.assign(
            cid_num=selected_info["container_id"].str.extract(r"c_(\d+)").astype(int)
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
    matched_containers_by_app: dict[str, set[str]] = defaultdict(set)
    service_accumulator: dict[tuple[str, int], dict[str, float]] = {}
    rows_scanned = 0
    rows_matched = 0
    max_seen_container_id = 0
    next_report_rows = 5_000_000

    response = None
    tar = None
    try:
        response, tar = open_tar_stream(str(usage_archive))
        member = next(m for m in tar if m.isfile() and m.name.endswith(".csv"))
        stream = tar.extractfile(member)
        if stream is None:
            raise FileNotFoundError(f"Could not extract CSV from {usage_archive}")

        chunk_iter = pd.read_csv(
            stream,
            header=None,
            names=USAGE_COLUMNS,
            usecols=["container_id", "time_stamp", "cpu_util_percent", "mem_util_percent"],
            chunksize=chunk_size,
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
            rows_scanned += len(chunk)
            max_seen_container_id = max(max_seen_container_id, int(chunk["numeric_id"].max()))

            view = chunk[chunk["container_id"].isin(selected_ids)].copy()
            if view.empty:
                continue
            view["app_du"] = view["container_id"].map(app_map)
            view = view.dropna(subset=["app_du"])
            if view.empty:
                continue
            view["time_stamp"] = pd.to_numeric(view["time_stamp"], errors="coerce")
            view["cpu_util_percent"] = pd.to_numeric(view["cpu_util_percent"], errors="coerce")
            view["mem_util_percent"] = pd.to_numeric(view["mem_util_percent"], errors="coerce")
            view = view.dropna(subset=["time_stamp", "cpu_util_percent", "mem_util_percent"])
            if view.empty:
                continue
            view["minute_index"] = (view["time_stamp"].astype("int64") // 60).astype("int64")

            for app_du, group in view.groupby("app_du"):
                seen_containers[app_du].update(group["container_id"].astype(str).unique().tolist())
                minute_values = group["minute_index"].astype("int64").unique().tolist()
                seen_minutes[app_du].update(minute_values)
                matched_rows_by_app[app_du] += len(group)
                local_min = int(group["minute_index"].min())
                local_max = int(group["minute_index"].max())
                if app_du not in min_minute or local_min < min_minute[app_du]:
                    min_minute[app_du] = local_min
                if app_du not in max_minute or local_max > max_minute[app_du]:
                    max_minute[app_du] = local_max

            view["cpu_request_cores"] = view["container_id"].map(cpu_map)
            view["mem_size"] = view["container_id"].map(mem_map)
            view["cpu_used_cores_proxy"] = view["cpu_request_cores"] * view["cpu_util_percent"] / 100.0
            container_minute = (
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
            rows_matched += len(container_minute)
            for app_du, container_ids in container_minute.groupby("app_du")["container_id"]:
                matched_containers_by_app[str(app_du)].update(container_ids.astype(str).unique().tolist())

            service_grouped = (
                container_minute.groupby(["app_du", "minute_index"], as_index=False)
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
            for row in service_grouped.itertuples(index=False):
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
            if rows_scanned >= next_report_rows:
                print(
                    (
                        "direct_broad_scan "
                        f"rows_scanned={rows_scanned} "
                        f"rows_matched={rows_matched} "
                        f"services_seen={len(seen_containers)} "
                        f"max_seen_container_id={max_seen_container_id}"
                    ),
                    flush=True,
                )
                next_report_rows += 5_000_000
    finally:
        if tar is not None:
            tar.close()
        if response is not None:
            response.close()

    profile_rows: list[dict] = []
    for app_du in sorted(seen_containers):
        minute_count = len(seen_minutes[app_du])
        span_minutes = max_minute[app_du] - min_minute[app_du] + 1
        total_containers = int(meta_lookup.loc[app_du, "unique_containers"])
        profile_rows.append(
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
                "profile_max_container_id": max_seen_container_id,
                "nonblank_rows_scanned": rows_scanned,
                "matched_rows_scanned": sum(matched_rows_by_app.values()),
            }
        )
    profile_df = pd.DataFrame(profile_rows)
    if not profile_df.empty:
        profile_df = profile_df.sort_values(
            ["container_hit_ratio", "minute_coverage_ratio", "usage_containers_seen"],
            ascending=[False, False, False],
        )
    profile_csv.parent.mkdir(parents=True, exist_ok=True)
    profile_df.to_csv(profile_csv, index=False)

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
    if not service_rows:
        raise ValueError("No service-level rows were aggregated during the full usage scan.")
    service_df = pd.DataFrame(service_rows).sort_values(["app_du", "minute_index"])
    service_df["service_cpu_utilization_weighted"] = np.where(
        service_df["service_cpu_request_cores_total"] > 1e-9,
        100.0
        * service_df["service_cpu_used_cores_proxy"]
        / service_df["service_cpu_request_cores_total"],
        np.nan,
    )

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
    summary_df = request_lookup.merge(matched_lookup, on="app_du", how="left")
    summary_df["matched_containers"] = summary_df["matched_containers"].fillna(0).astype(int)
    return service_df, summary_df, rows_scanned, rows_matched, max_seen_container_id


def aggregate_candidate_service_single_pass(
    usage_archive: Path,
    selected_info: pd.DataFrame,
    chunk_size: int,
) -> tuple[pd.DataFrame, pd.DataFrame, int, int, int]:
    app_map = selected_info.set_index("container_id")["app_du"].to_dict()
    cpu_map = selected_info.set_index("container_id")["cpu_request_cores"].to_dict()
    mem_map = selected_info.set_index("container_id")["mem_size"].to_dict()
    selected_ids = set(app_map)

    matched_containers_by_app: dict[str, set[str]] = defaultdict(set)
    service_accumulator: dict[tuple[str, int], dict[str, float]] = {}
    rows_scanned = 0
    rows_matched = 0
    max_seen_container_id = 0
    next_report_rows = 5_000_000

    response = None
    tar = None
    try:
        response, tar = open_tar_stream(str(usage_archive))
        member = next(m for m in tar if m.isfile() and m.name.endswith(".csv"))
        stream = tar.extractfile(member)
        if stream is None:
            raise FileNotFoundError(f"Could not extract CSV from {usage_archive}")

        chunk_iter = pd.read_csv(
            stream,
            header=None,
            names=USAGE_COLUMNS,
            usecols=["container_id", "time_stamp", "cpu_util_percent", "mem_util_percent"],
            chunksize=chunk_size,
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
            rows_scanned += len(chunk)
            max_seen_container_id = max(max_seen_container_id, int(chunk["numeric_id"].max()))

            view = chunk[chunk["container_id"].isin(selected_ids)].copy()
            if view.empty:
                continue
            view["app_du"] = view["container_id"].map(app_map)
            view = view.dropna(subset=["app_du"])
            if view.empty:
                continue
            view["time_stamp"] = pd.to_numeric(view["time_stamp"], errors="coerce")
            view["cpu_util_percent"] = pd.to_numeric(view["cpu_util_percent"], errors="coerce")
            view["mem_util_percent"] = pd.to_numeric(view["mem_util_percent"], errors="coerce")
            view = view.dropna(subset=["time_stamp", "cpu_util_percent", "mem_util_percent"])
            if view.empty:
                continue
            view["minute_index"] = (view["time_stamp"].astype("int64") // 60).astype("int64")
            view["cpu_request_cores"] = view["container_id"].map(cpu_map)
            view["mem_size"] = view["container_id"].map(mem_map)
            view["cpu_used_cores_proxy"] = view["cpu_request_cores"] * view["cpu_util_percent"] / 100.0
            container_minute = (
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
            rows_matched += len(container_minute)
            for app_du, container_ids in container_minute.groupby("app_du")["container_id"]:
                matched_containers_by_app[str(app_du)].update(container_ids.astype(str).unique().tolist())

            service_grouped = (
                container_minute.groupby(["app_du", "minute_index"], as_index=False)
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
            for row in service_grouped.itertuples(index=False):
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
            if rows_scanned >= next_report_rows:
                print(
                    (
                        "candidate_broad_scan "
                        f"rows_scanned={rows_scanned} "
                        f"rows_matched={rows_matched} "
                        f"services_selected={selected_info['app_du'].nunique()} "
                        f"max_seen_container_id={max_seen_container_id}"
                    ),
                    flush=True,
                )
                next_report_rows += 5_000_000
    finally:
        if tar is not None:
            tar.close()
        if response is not None:
            response.close()

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
    if not service_rows:
        raise ValueError("No service-level rows were aggregated for the broad candidate services.")
    service_df = pd.DataFrame(service_rows).sort_values(["app_du", "minute_index"])
    service_df["service_cpu_utilization_weighted"] = np.where(
        service_df["service_cpu_request_cores_total"] > 1e-9,
        100.0
        * service_df["service_cpu_used_cores_proxy"]
        / service_df["service_cpu_request_cores_total"],
        np.nan,
    )

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
    summary_df = request_lookup.merge(matched_lookup, on="app_du", how="left")
    summary_df["matched_containers"] = summary_df["matched_containers"].fillna(0).astype(int)
    return service_df, summary_df, rows_scanned, rows_matched, max_seen_container_id


def finalize_service_cohort_from_aggregates(
    service_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    selected_info: pd.DataFrame,
    selected_apps: list[str],
    rows_scanned: int,
    rows_matched: int,
    max_seen_container_id: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    selected_set = set(selected_apps)
    service_df = service_df[service_df["app_du"].isin(selected_set)].copy()
    summary_df = summary_df[summary_df["app_du"].isin(selected_set)].copy()
    if service_df.empty or summary_df.empty:
        raise ValueError("No candidate services remain for broad cohort construction.")

    global_start = int(service_df["minute_index"].min())
    global_end = int(service_df["minute_index"].max())
    full_index = pd.Index(range(global_start, global_end + 1), name="minute_index")
    span = len(full_index)

    filled_parts: list[pd.DataFrame] = []
    summary_rows: list[dict] = []
    for app_du, group in service_df.groupby("app_du"):
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
    detail_summary_df = pd.DataFrame(summary_rows)
    final_summary_df = detail_summary_df.merge(summary_df, on="app_du", how="left")
    final_summary_df["matched_containers"] = final_summary_df["matched_containers"].fillna(0).astype(int)
    final_summary_df["unique_containers"] = final_summary_df["unique_containers"].fillna(0).astype(int)
    final_summary_df["container_hit_ratio"] = np.where(
        final_summary_df["unique_containers"] > 0,
        final_summary_df["matched_containers"] / final_summary_df["unique_containers"],
        np.nan,
    )
    final_summary_df["usage_rows_scanned"] = rows_scanned
    final_summary_df["matched_container_minute_rows"] = rows_matched
    final_summary_df["max_seen_container_id"] = max_seen_container_id
    final_summary_df = final_summary_df.drop(columns=["min_selected_ts", "max_selected_ts"])
    return filled_df, final_summary_df.sort_values("coverage_ratio", ascending=False)


def build_overlap_audit(
    top10_apps: list[str],
    meta_candidates: pd.DataFrame,
    profile_df: pd.DataFrame,
    extracted_summary_df: pd.DataFrame,
    final_summary_df: pd.DataFrame,
    min_coverage_ratio: float,
    min_container_hit_ratio: float,
) -> pd.DataFrame:
    meta_candidate_set = set(meta_candidates["app_du"])
    profiled_set = set(profile_df["app_du"])
    extracted_lookup = extracted_summary_df.set_index("app_du") if not extracted_summary_df.empty else pd.DataFrame()
    final_set = set(final_summary_df["app_du"])

    rows: list[dict] = []
    for app_du in top10_apps:
        coverage_ratio = None
        container_hit_ratio = None
        if not extracted_summary_df.empty and app_du in extracted_lookup.index:
            coverage_ratio = float(extracted_lookup.loc[app_du, "coverage_ratio"])
            container_hit_ratio = float(extracted_lookup.loc[app_du, "container_hit_ratio"])

        if app_du in final_set:
            status = "retained"
            reason = ""
        elif app_du not in meta_candidate_set:
            status = "excluded"
            reason = "failed_meta_prefilter"
        elif app_du not in profiled_set:
            status = "excluded"
            reason = "no_usage_rows_in_full_scan"
        elif app_du not in extracted_lookup.index:
            status = "excluded"
            reason = "no_container_minute_rows_after_extraction"
        else:
            reasons: list[str] = []
            if coverage_ratio is not None and coverage_ratio < min_coverage_ratio:
                reasons.append(f"coverage_ratio<{min_coverage_ratio:.2f} ({coverage_ratio:.4f})")
            if container_hit_ratio is not None and container_hit_ratio < min_container_hit_ratio:
                reasons.append(
                    f"container_hit_ratio<{min_container_hit_ratio:.2f} ({container_hit_ratio:.4f})"
                )
            status = "excluded"
            reason = "; ".join(reasons) if reasons else "excluded_by_final_filter"

        rows.append(
            {
                "app_du": app_du,
                "in_top10": True,
                "in_meta_prefilter": app_du in meta_candidate_set,
                "in_full_profile": app_du in profiled_set,
                "in_broad": app_du in final_set,
                "status": status,
                "reason_if_excluded": reason,
                "coverage_ratio": coverage_ratio,
                "container_hit_ratio": container_hit_ratio,
            }
        )

    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--meta-tar", type=Path, required=True)
    parser.add_argument("--usage-archive", type=Path, required=True)
    parser.add_argument("--profile-csv", type=Path, required=True)
    parser.add_argument("--candidate-apps-file", type=Path, required=True)
    parser.add_argument("--filtered-csv", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--summary-csv", type=Path, required=True)
    parser.add_argument("--overlap-audit-csv", type=Path, required=True)
    parser.add_argument("--top10-summary-csv", type=Path, required=True)
    parser.add_argument("--min-span-seconds", type=int, default=650_000)
    parser.add_argument("--min-containers", type=int, default=60)
    parser.add_argument("--min-coverage-ratio", type=float, default=0.96)
    parser.add_argument("--min-container-hit-ratio", type=float, default=0.90)
    parser.add_argument("--chunk-size", type=int, default=400_000)
    parser.add_argument("--reuse-profile", action="store_true")
    parser.add_argument("--reuse-filtered-csv", action="store_true")
    parser.add_argument("--skip-archive-check", action="store_true")
    args = parser.parse_args()

    if not args.skip_archive_check:
        validate_local_usage_archive(args.usage_archive)

    container_info, app_summary = read_container_meta(args.meta_tar)
    meta_candidates = (
        app_summary[
            (app_summary["span_seconds"] >= args.min_span_seconds)
            & (app_summary["unique_containers"] >= args.min_containers)
        ]
        .copy()
        .sort_values(["unique_containers", "span_seconds"], ascending=[False, False])
    )
    meta_candidate_set = set(meta_candidates["app_du"])

    selected_info_all = container_info[container_info["app_du"].isin(meta_candidates["app_du"])].copy()
    rows_scanned = pd.NA
    rows_matched = pd.NA
    max_seen_container_id = pd.NA
    if args.reuse_profile and args.profile_csv.exists():
        profile_df = pd.read_csv(args.profile_csv)
    else:
        profile_df, service_df_all, broad_summary_all, rows_scanned, rows_matched, max_seen_container_id = profile_and_build_cohort_single_pass(
            usage_archive=args.usage_archive,
            selected_info=selected_info_all,
            profile_csv=args.profile_csv,
            chunk_size=args.chunk_size,
        )

    profiled_eligible = profile_df[profile_df["container_hit_ratio"] >= args.min_container_hit_ratio].copy()
    candidate_apps = [app_du for app_du in profiled_eligible["app_du"].tolist() if app_du in meta_candidate_set]
    args.candidate_apps_file.parent.mkdir(parents=True, exist_ok=True)
    args.candidate_apps_file.write_text("".join(f"{app_du}\n" for app_du in candidate_apps), encoding="utf-8")

    if not candidate_apps:
        raise ValueError("No app_du remains after the meta prefilter and full profile scan.")

    selected_info = selected_info_all[selected_info_all["app_du"].isin(candidate_apps)].copy()
    if args.reuse_profile and args.profile_csv.exists() and args.reuse_filtered_csv and args.filtered_csv.exists():
        broad_df_all, broad_summary_all = build_service_cohort(
            args.filtered_csv,
            selected_info,
            selected_apps=set(candidate_apps),
            chunk_size=args.chunk_size,
        )
        broad_summary_all["usage_rows_scanned"] = rows_scanned
        broad_summary_all["matched_container_minute_rows"] = rows_matched
        broad_summary_all["max_seen_container_id"] = max_seen_container_id
    elif args.reuse_profile and args.profile_csv.exists():
        service_df_all, candidate_summary_all, rows_scanned, rows_matched, max_seen_container_id = aggregate_candidate_service_single_pass(
            usage_archive=args.usage_archive,
            selected_info=selected_info,
            chunk_size=args.chunk_size,
        )
        broad_df_all, broad_summary_all = finalize_service_cohort_from_aggregates(
            service_df=service_df_all,
            summary_df=candidate_summary_all,
            selected_info=selected_info,
            selected_apps=candidate_apps,
            rows_scanned=int(rows_scanned),
            rows_matched=int(rows_matched),
            max_seen_container_id=int(max_seen_container_id),
        )
    else:
        broad_df_all, broad_summary_all = finalize_service_cohort_from_aggregates(
            service_df=service_df_all,
            summary_df=broad_summary_all,
            selected_info=selected_info,
            selected_apps=candidate_apps,
            rows_scanned=int(rows_scanned),
            rows_matched=int(rows_matched),
            max_seen_container_id=int(max_seen_container_id),
        )

    final_summary_df = broad_summary_all[
        (broad_summary_all["coverage_ratio"] >= args.min_coverage_ratio)
        & (broad_summary_all["container_hit_ratio"] >= args.min_container_hit_ratio)
    ].copy()
    final_summary_df = final_summary_df.sort_values(
        ["coverage_ratio", "container_hit_ratio", "mean_service_cpu_used_cores_proxy"],
        ascending=[False, False, False],
    )
    final_apps = final_summary_df["app_du"].tolist()
    final_df = broad_df_all[broad_df_all["app_du"].isin(final_apps)].copy()

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(args.output_csv, index=False)
    args.summary_csv.parent.mkdir(parents=True, exist_ok=True)
    final_summary_df.to_csv(args.summary_csv, index=False)

    top10_apps = pd.read_csv(args.top10_summary_csv)["app_du"].tolist()
    overlap_df = build_overlap_audit(
        top10_apps=top10_apps,
        meta_candidates=meta_candidates,
        profile_df=profile_df,
        extracted_summary_df=broad_summary_all,
        final_summary_df=final_summary_df,
        min_coverage_ratio=args.min_coverage_ratio,
        min_container_hit_ratio=args.min_container_hit_ratio,
    )
    args.overlap_audit_csv.parent.mkdir(parents=True, exist_ok=True)
    overlap_df.to_csv(args.overlap_audit_csv, index=False)


if __name__ == "__main__":
    main()
