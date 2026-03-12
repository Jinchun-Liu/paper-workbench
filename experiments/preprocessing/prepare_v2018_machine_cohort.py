#!/usr/bin/env python3
"""Build a high-coverage machine cohort dataset from Alibaba machine_usage.tar.gz."""

from __future__ import annotations

import argparse
import tarfile
from collections import Counter
from pathlib import Path

import pandas as pd


RAW_COLUMNS = [
    "machine_id",
    "time_stamp",
    "cpu_util_percent",
    "mem_util_percent",
    "unused_4",
    "unused_5",
    "unused_6",
    "unused_7",
    "unused_8",
]


def open_member_stream(tar_path: Path):
    tar = tarfile.open(tar_path, mode="r:gz")
    members = [member for member in tar.getmembers() if member.isfile() and member.name.endswith(".csv")]
    if not members:
        raise FileNotFoundError(f"No CSV file found in {tar_path}")
    stream = tar.extractfile(members[0])
    if stream is None:
        raise FileNotFoundError(f"Could not extract {members[0].name} from {tar_path}")
    return tar, stream


def select_top_machines(input_tar: Path, chunk_size: int, top_n: int) -> list[str]:
    counts: Counter[str] = Counter()
    tar, stream = open_member_stream(input_tar)
    try:
        for chunk in pd.read_csv(
            stream,
            header=None,
            usecols=[0],
            names=["machine_id"],
            chunksize=chunk_size,
        ):
            counts.update(chunk["machine_id"].astype(str))
    finally:
        stream.close()
        tar.close()
    return [machine_id for machine_id, _ in counts.most_common(top_n)]


def extract_machine_minutes(input_tar: Path, machine_ids: list[str], chunk_size: int) -> pd.DataFrame:
    target_ids = set(machine_ids)
    partials: list[pd.DataFrame] = []
    tar, stream = open_member_stream(input_tar)
    try:
        for chunk in pd.read_csv(
            stream,
            header=None,
            usecols=[0, 1, 2, 3],
            names=["machine_id", "time_stamp", "cpu_util_percent", "mem_util_percent"],
            chunksize=chunk_size,
        ):
            view = chunk[chunk["machine_id"].isin(target_ids)].copy()
            if view.empty:
                continue
            view["time_stamp"] = pd.to_numeric(view["time_stamp"], errors="coerce")
            view["cpu_util_percent"] = pd.to_numeric(view["cpu_util_percent"], errors="coerce")
            view["mem_util_percent"] = pd.to_numeric(view["mem_util_percent"], errors="coerce")
            view = view.dropna()
            if view.empty:
                continue
            view["minute_index"] = (view["time_stamp"].astype("int64") // 60).astype("int64")
            grouped = (
                view.groupby(["machine_id", "minute_index"], as_index=False)
                .agg(
                    cpu_utilization_mean=("cpu_util_percent", "mean"),
                    memory_utilization_mean=("mem_util_percent", "mean"),
                    observation_count=("cpu_util_percent", "size"),
                )
            )
            partials.append(grouped)
    finally:
        stream.close()
        tar.close()

    if not partials:
        raise ValueError("No machine-level minutes were extracted from the input tar.")

    result = pd.concat(partials, ignore_index=True)
    return (
        result.groupby(["machine_id", "minute_index"], as_index=False)
        .agg(
            cpu_utilization_mean=("cpu_utilization_mean", "mean"),
            memory_utilization_mean=("memory_utilization_mean", "mean"),
            observation_count=("observation_count", "sum"),
        )
        .sort_values(["machine_id", "minute_index"])
    )


def finalize_dataset(
    minute_df: pd.DataFrame,
    min_coverage_ratio: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    global_start = int(minute_df["minute_index"].min())
    global_end = int(minute_df["minute_index"].max())
    full_index = pd.Index(range(global_start, global_end + 1), name="minute_index")
    span = len(full_index)

    summary = (
        minute_df.groupby("machine_id")
        .agg(
            observed_minutes=("minute_index", "nunique"),
            mean_cpu=("cpu_utilization_mean", "mean"),
            std_cpu=("cpu_utilization_mean", "std"),
            mean_memory=("memory_utilization_mean", "mean"),
            avg_observations_per_minute=("observation_count", "mean"),
        )
        .reset_index()
    )
    summary["coverage_ratio"] = summary["observed_minutes"] / span
    retained_ids = summary.loc[summary["coverage_ratio"] >= min_coverage_ratio, "machine_id"].tolist()
    if not retained_ids:
        raise ValueError("No machine meets the requested coverage threshold.")

    summary = summary[summary["machine_id"].isin(retained_ids)].copy()

    filled_parts: list[pd.DataFrame] = []
    for machine_id in retained_ids:
        entity = minute_df[minute_df["machine_id"] == machine_id].copy()
        entity = entity.set_index("minute_index").sort_index()
        entity = entity.reindex(full_index)
        missing_mask = entity["cpu_utilization_mean"].isna() | entity["memory_utilization_mean"].isna()
        entity["cpu_utilization_mean"] = entity["cpu_utilization_mean"].interpolate(limit_direction="both")
        entity["memory_utilization_mean"] = entity["memory_utilization_mean"].interpolate(limit_direction="both")
        entity["observation_count"] = entity["observation_count"].fillna(0).astype(int)
        entity["imputed"] = missing_mask.astype(int)
        entity["machine_id"] = machine_id
        filled_parts.append(entity.reset_index())

    filled_df = pd.concat(filled_parts, ignore_index=True)
    imputed_ratio = (
        filled_df.groupby("machine_id")["imputed"]
        .mean()
        .reset_index()
        .rename(columns={"imputed": "imputed_ratio"})
    )
    summary = summary.merge(imputed_ratio, on="machine_id", how="left")
    summary["global_minute_start"] = global_start
    summary["global_minute_end"] = global_end
    summary["global_span_minutes"] = span
    return filled_df, summary.sort_values("coverage_ratio", ascending=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-tar", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--summary-csv", type=Path, required=True)
    parser.add_argument("--chunk-size", type=int, default=750_000)
    parser.add_argument("--top-n", type=int, default=12)
    parser.add_argument("--min-coverage-ratio", type=float, default=0.93)
    args = parser.parse_args()

    top_machines = select_top_machines(args.input_tar, args.chunk_size, args.top_n)
    minute_df = extract_machine_minutes(args.input_tar, top_machines, args.chunk_size)
    filled_df, summary_df = finalize_dataset(minute_df, args.min_coverage_ratio)

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    filled_df.to_csv(args.output_csv, index=False)
    args.summary_csv.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(args.summary_csv, index=False)


if __name__ == "__main__":
    main()
