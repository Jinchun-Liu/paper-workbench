#!/usr/bin/env python3
"""Build a one-minute aggregate workload series from Alibaba machine_usage.tar.gz."""

from __future__ import annotations

import argparse
import io
import tarfile
from pathlib import Path

import pandas as pd


EXPECTED_COLUMNS = [
    "machine_id",
    "time_stamp",
    "cpu_util_percent",
    "mem_util_percent",
]

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


def open_member_stream(tar_path: Path) -> io.BufferedReader:
    tar = tarfile.open(tar_path, mode="r:gz")
    members = [m for m in tar.getmembers() if m.isfile() and m.name.endswith(".csv")]
    if not members:
        raise FileNotFoundError(f"No CSV file found in {tar_path}")
    member = members[0]
    stream = tar.extractfile(member)
    if stream is None:
        raise FileNotFoundError(f"Could not extract {member.name} from {tar_path}")
    return tar, stream


def build_series(input_tar: Path, output_csv: Path, chunk_size: int) -> None:
    tar, stream = open_member_stream(input_tar)
    partials: list[pd.DataFrame] = []
    try:
        for chunk in pd.read_csv(
            stream,
            header=None,
            names=RAW_COLUMNS,
            usecols=[0, 1, 2, 3],
            chunksize=chunk_size,
        ):
            view = chunk[EXPECTED_COLUMNS].copy()
            view["cpu_util_percent"] = pd.to_numeric(view["cpu_util_percent"], errors="coerce")
            view["mem_util_percent"] = pd.to_numeric(view["mem_util_percent"], errors="coerce")
            view["time_stamp"] = pd.to_numeric(view["time_stamp"], errors="coerce")
            view = view.dropna()
            view["cpu_sum"] = view["cpu_util_percent"]
            view["mem_sum"] = view["mem_util_percent"]
            view["row_count"] = 1
            grouped = (
                view.groupby("time_stamp", as_index=False)
                .agg(
                    cpu_sum=("cpu_sum", "sum"),
                    mem_sum=("mem_sum", "sum"),
                    active_machine_count=("row_count", "sum"),
                )
            )
            partials.append(grouped)
    finally:
        stream.close()
        tar.close()

    if not partials:
        raise ValueError("No usable rows were parsed from the tar archive.")

    merged = pd.concat(partials, ignore_index=True)
    merged = (
        merged.groupby("time_stamp", as_index=False)
        .agg(
            cpu_sum=("cpu_sum", "sum"),
            mem_sum=("mem_sum", "sum"),
            active_machine_count=("active_machine_count", "sum"),
        )
        .sort_values("time_stamp")
    )
    merged["cluster_cpu_utilization_mean"] = merged["cpu_sum"] / merged["active_machine_count"]
    merged["cluster_memory_utilization_mean"] = merged["mem_sum"] / merged["active_machine_count"]
    merged["minute_index"] = (merged["time_stamp"] // 60).astype(int)
    resampled = (
        merged.groupby("minute_index", as_index=False)
        .agg(
            cluster_cpu_utilization_mean=("cluster_cpu_utilization_mean", "mean"),
            cluster_memory_utilization_mean=("cluster_memory_utilization_mean", "mean"),
            active_machine_count=("active_machine_count", "mean"),
        )
        .sort_values("minute_index")
    )
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    resampled.to_csv(output_csv, index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-tar", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--chunk-size", type=int, default=500_000)
    args = parser.parse_args()
    build_series(args.input_tar, args.output_csv, args.chunk_size)


if __name__ == "__main__":
    main()
