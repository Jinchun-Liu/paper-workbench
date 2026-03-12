#!/usr/bin/env python3
"""Run the broad service-cohort build, experiments, and stability analysis."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run_step(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    data_processed = repo_root / "data" / "processed"
    results_root = repo_root / "experiments" / "results"
    parser = argparse.ArgumentParser()
    parser.add_argument("--python-executable", type=Path, default=Path(sys.executable))
    parser.add_argument("--meta-tar", type=Path, default=repo_root / "data" / "raw" / "container_meta.tar.gz")
    parser.add_argument(
        "--usage-archive",
        type=Path,
        default=repo_root / "data" / "raw" / "container_usage.tar.gz",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=repo_root / "experiments" / "configs" / "default_v2018.yaml",
    )
    parser.add_argument(
        "--top10-summary-csv",
        type=Path,
        default=data_processed / "service_cohort_top10_summary_v2018.csv",
    )
    parser.add_argument(
        "--top10-forecast-raw",
        type=Path,
        default=results_root / "service_cohort_top10" / "tables" / "service_forecasting_raw.csv",
    )
    parser.add_argument(
        "--top10-policy-raw",
        type=Path,
        default=results_root / "service_cohort_top10" / "tables" / "service_policy_raw.csv",
    )
    parser.add_argument(
        "--profile-csv",
        type=Path,
        default=data_processed / "service_profile_full_v2018.csv",
    )
    parser.add_argument(
        "--candidate-apps-file",
        type=Path,
        default=data_processed / "service_candidate_apps_broad_v2018.txt",
    )
    parser.add_argument(
        "--filtered-csv",
        type=Path,
        default=data_processed / "service_cohort_broad_filtered_container_usage.csv",
    )
    parser.add_argument(
        "--broad-service-csv",
        type=Path,
        default=data_processed / "service_cohort_broad_v2018.csv",
    )
    parser.add_argument(
        "--broad-summary-csv",
        type=Path,
        default=data_processed / "service_cohort_broad_summary_v2018.csv",
    )
    parser.add_argument(
        "--overlap-audit-csv",
        type=Path,
        default=data_processed / "service_cohort_top10_overlap_audit.csv",
    )
    parser.add_argument(
        "--broad-output-dir",
        type=Path,
        default=results_root / "service_cohort_broad",
    )
    parser.add_argument("--bootstrap-seed", type=int, default=20260311)
    parser.add_argument("--bootstrap-resamples", type=int, default=10_000)
    parser.add_argument("--reuse-profile", action="store_true")
    parser.add_argument("--reuse-filtered-csv", action="store_true")
    parser.add_argument("--skip-archive-check", action="store_true")
    args = parser.parse_args()

    python_executable = str(args.python_executable)
    build_script = repo_root / "experiments" / "preprocessing" / "build_broad_service_cohort.py"
    experiment_script = repo_root / "experiments" / "run_container_service_experiments.py"
    stability_script = repo_root / "experiments" / "analyze_service_cohort_stability.py"

    build_cmd = [
        python_executable,
        str(build_script),
        "--meta-tar",
        str(args.meta_tar),
        "--usage-archive",
        str(args.usage_archive),
        "--profile-csv",
        str(args.profile_csv),
        "--candidate-apps-file",
        str(args.candidate_apps_file),
        "--filtered-csv",
        str(args.filtered_csv),
        "--output-csv",
        str(args.broad_service_csv),
        "--summary-csv",
        str(args.broad_summary_csv),
        "--overlap-audit-csv",
        str(args.overlap_audit_csv),
        "--top10-summary-csv",
        str(args.top10_summary_csv),
    ]
    if args.reuse_profile:
        build_cmd.append("--reuse-profile")
    if args.reuse_filtered_csv:
        build_cmd.append("--reuse-filtered-csv")
    if args.skip_archive_check:
        build_cmd.append("--skip-archive-check")
    run_step(build_cmd)

    run_step(
        [
            python_executable,
            str(experiment_script),
            "--config",
            str(args.config),
            "--service-csv",
            str(args.broad_service_csv),
            "--service-summary-csv",
            str(args.broad_summary_csv),
            "--output-dir",
            str(args.broad_output_dir),
        ]
    )

    run_step(
        [
            python_executable,
            str(stability_script),
            "--top10-forecast-raw",
            str(args.top10_forecast_raw),
            "--top10-policy-raw",
            str(args.top10_policy_raw),
            "--top10-summary-csv",
            str(args.top10_summary_csv),
            "--broad-forecast-raw",
            str(args.broad_output_dir / "tables" / "service_forecasting_raw.csv"),
            "--broad-policy-raw",
            str(args.broad_output_dir / "tables" / "service_policy_raw.csv"),
            "--broad-summary-csv",
            str(args.broad_summary_csv),
            "--output-dir",
            str(args.broad_output_dir),
            "--bootstrap-seed",
            str(args.bootstrap_seed),
            "--bootstrap-resamples",
            str(args.bootstrap_resamples),
        ]
    )


if __name__ == "__main__":
    main()
