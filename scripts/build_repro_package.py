#!/usr/bin/env python3
"""Stage a frozen reproducibility package from a manifest."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import shutil
import tarfile
from typing import Iterable

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("submission/reproducibility-package-manifest.yaml"),
        help="Manifest YAML relative to the repository root.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output directory for the staged package.",
    )
    parser.add_argument(
        "--archive",
        action="store_true",
        help="Create a .tar.gz archive next to the staged directory.",
    )
    return parser.parse_args()


def sha256sum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_globs(patterns: Iterable[str]) -> list[str]:
    return [pattern.replace(os.sep, "/") for pattern in patterns]


def is_excluded(relative_path: Path, exclude_globs: list[str]) -> bool:
    rel = relative_path.as_posix()
    for pattern in exclude_globs:
        if fnmatch.fnmatch(rel, pattern):
            return True
        if rel.startswith(pattern.rstrip("*")) and pattern.endswith("/**"):
            return True
    return False


def copy_path(
    source_root: Path,
    rel_path: Path,
    output_root: Path,
    exclude_globs: list[str],
) -> None:
    source_path = source_root / rel_path
    target_path = output_root / rel_path
    if source_path.is_dir():
        for child in sorted(source_path.rglob("*")):
            if child.is_dir():
                continue
            child_rel = child.relative_to(source_root)
            if is_excluded(child_rel, exclude_globs):
                continue
            destination = output_root / child_rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(child, destination)
    else:
        if is_excluded(rel_path, exclude_globs):
            return
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)


def build_manifest(output_root: Path) -> tuple[list[dict[str, object]], int]:
    entries: list[dict[str, object]] = []
    total_bytes = 0
    for path in sorted(output_root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(output_root)
        size = path.stat().st_size
        total_bytes += size
        entries.append(
            {
                "path": rel.as_posix(),
                "bytes": size,
                "sha256": sha256sum(path),
            }
        )
    return entries, total_bytes


def write_checksums(output_root: Path, entries: list[dict[str, object]]) -> None:
    lines = [f"{entry['sha256']}  {entry['path']}" for entry in entries]
    (output_root / "SHA256SUMS").write_text("\n".join(lines) + "\n")


def write_build_metadata(
    output_root: Path,
    package_name: str,
    package_version: str,
    source_root: Path,
    include_paths: list[str],
    exclude_globs: list[str],
    entries: list[dict[str, object]],
    total_bytes: int,
) -> None:
    metadata = {
        "package_name": package_name,
        "package_version": package_version,
        "source_root": str(source_root),
        "include_paths": include_paths,
        "exclude_globs": exclude_globs,
        "file_count": len(entries),
        "total_bytes": total_bytes,
    }
    (output_root / "BUILD-METADATA.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n"
    )


def create_archive(output_root: Path) -> Path:
    archive_path = output_root.with_suffix(".tar.gz")
    with tarfile.open(archive_path, "w:gz") as archive:
        archive.add(output_root, arcname=output_root.name)
    return archive_path


def main() -> int:
    args = parse_args()
    source_root = args.manifest.resolve().parents[1]
    manifest = yaml.safe_load(args.manifest.read_text())

    package_name = manifest["package_name"]
    package_version = manifest["package_version"]
    include_paths = [str(path) for path in manifest["include_paths"]]
    exclude_globs = normalize_globs(manifest.get("exclude_globs", []))

    output_root = args.output.resolve()
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    for include_path in include_paths:
        copy_path(source_root, Path(include_path), output_root, exclude_globs)

    entries, total_bytes = build_manifest(output_root)
    write_checksums(output_root, entries)
    write_build_metadata(
        output_root,
        package_name,
        package_version,
        source_root,
        include_paths,
        exclude_globs,
        entries,
        total_bytes,
    )

    if args.archive:
        archive_path = create_archive(output_root)
        print(f"[archive] {archive_path}")

    print(f"[ok] staged {len(entries)} files ({total_bytes} bytes) at {output_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
