#!/usr/bin/env python3
"""Build a self-contained Cluster Computing LaTeX source package."""

from __future__ import annotations

import argparse
import fnmatch
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
import zipfile

import yaml


INPUT_RE = re.compile(r"\\(input|include)\s*\{([^}]+)\}")
BIB_RE = re.compile(r"\\bibliography\s*\{([^}]+)\}")
GRAPHICS_RE = re.compile(
    r"(?P<prefix>\\includegraphics(?:\s*\[[^]]*\])?\s*)\{(?P<path>[^}]+)\}"
)
DOC_CLASS_RE = re.compile(r"\\documentclass(?:\[[^]]*\])?\s*\{([^}]+)\}")
GRAPHICS_EXTENSIONS = (".pdf", ".png", ".jpg", ".jpeg", ".eps")


@dataclass
class DependencyState:
    tex_files: set[Path] = field(default_factory=set)
    bib_files: set[Path] = field(default_factory=set)
    figure_files: dict[Path, str] = field(default_factory=dict)
    figure_name_sources: dict[str, Path] = field(default_factory=dict)
    class_names: set[str] = field(default_factory=set)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("submission/cluster-source-package-manifest.yaml"),
        help="Manifest YAML relative to the repository root.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("submission/source-package/cluster-computing"),
        help="Output directory for the staged source package.",
    )
    parser.add_argument(
        "--archive",
        action="store_true",
        help="Create a .zip archive next to the staged directory after verification.",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify the staged package by compiling it in a clean temporary directory.",
    )
    return parser.parse_args()


def normalize_globs(patterns: Iterable[str]) -> list[str]:
    return [pattern.replace("\\", "/") for pattern in patterns]


def is_excluded(relative_path: Path, exclude_globs: list[str]) -> bool:
    rel = relative_path.as_posix()
    for pattern in exclude_globs:
        if fnmatch.fnmatch(rel, pattern):
            return True
        if rel.startswith(pattern.rstrip("*")) and pattern.endswith("/**"):
            return True
    return False


def strip_comments(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        pieces: list[str] = []
        escaped = False
        for char in line:
            if char == "%" and not escaped:
                break
            pieces.append(char)
            escaped = char == "\\" and not escaped
            if char != "\\":
                escaped = False
        lines.append("".join(pieces))
    return "\n".join(lines)


def split_code_and_comment(line: str) -> tuple[str, str]:
    escaped = False
    for index, char in enumerate(line):
        if char == "%" and not escaped:
            return line[:index], line[index:]
        escaped = char == "\\" and not escaped
        if char != "\\":
            escaped = False
    return line, ""


def resolve_with_candidates(
    base_dirs: Iterable[Path],
    ref: str,
    suffixes: Iterable[str],
) -> Path:
    candidate_bases = [base.resolve() for base in base_dirs]
    for base_dir in candidate_bases:
        candidate = (base_dir / ref).resolve()
        if Path(ref).suffix:
            if candidate.is_file():
                return candidate
            continue
        for suffix in suffixes:
            with_suffix = candidate.with_suffix(suffix)
            if with_suffix.is_file():
                return with_suffix
    bases = ", ".join(str(path) for path in candidate_bases)
    raise FileNotFoundError(f"unresolved dependency: {ref} from [{bases}]")


def resolve_tex_dependency(document_root: Path, source_file: Path, ref: str) -> Path:
    return resolve_with_candidates((document_root, source_file.parent), ref.strip(), (".tex",))


def resolve_bibliography_dependencies(
    document_root: Path,
    source_file: Path,
    ref_group: str,
) -> list[Path]:
    refs = [item.strip() for item in ref_group.split(",") if item.strip()]
    return [
        resolve_with_candidates((document_root, source_file.parent), ref, (".bib",))
        for ref in refs
    ]


def resolve_graphics_dependency(document_root: Path, source_file: Path, ref: str) -> Path:
    return resolve_with_candidates(
        (document_root, source_file.parent),
        ref.strip(),
        GRAPHICS_EXTENSIONS,
    )


def discover_dependencies(
    repo_root: Path,
    entry_file: Path,
    document_root: Path,
    exclude_globs: list[str],
) -> DependencyState:
    state = DependencyState()
    pending = [entry_file]
    seen: set[Path] = set()

    while pending:
        source_file = pending.pop()
        source_file = source_file.resolve()
        if source_file in seen:
            continue
        seen.add(source_file)

        relative_repo_path = source_file.relative_to(repo_root)
        if is_excluded(relative_repo_path, exclude_globs):
            raise RuntimeError(f"entry dependency matched excluded pattern: {relative_repo_path}")

        state.tex_files.add(source_file)
        text = source_file.read_text()
        parsed_text = strip_comments(text)

        for class_name in DOC_CLASS_RE.findall(parsed_text):
            state.class_names.add(class_name.strip())

        for _, ref in INPUT_RE.findall(parsed_text):
            dependency = resolve_tex_dependency(document_root, source_file, ref)
            pending.append(dependency)

        for ref_group in BIB_RE.findall(parsed_text):
            for dependency in resolve_bibliography_dependencies(
                document_root,
                source_file,
                ref_group,
            ):
                relative_dep = dependency.relative_to(repo_root)
                if is_excluded(relative_dep, exclude_globs):
                    raise RuntimeError(
                        f"bibliography dependency matched excluded pattern: {relative_dep}"
                    )
                state.bib_files.add(dependency)

        for match in GRAPHICS_RE.finditer(parsed_text):
            dependency = resolve_graphics_dependency(
                document_root,
                source_file,
                match.group("path"),
            )
            relative_dep = dependency.relative_to(repo_root)
            if is_excluded(relative_dep, exclude_globs):
                raise RuntimeError(
                    f"figure dependency matched excluded pattern: {relative_dep}"
                )
            basename = dependency.name
            prior_source = state.figure_name_sources.get(basename)
            if prior_source and prior_source != dependency:
                raise RuntimeError(
                    "figure basename collision detected: "
                    f"{basename} from {prior_source} and {dependency}"
                )
            state.figure_name_sources[basename] = dependency
            state.figure_files[dependency] = basename

    return state


def package_relative_path(manuscript_root: Path, source_path: Path) -> Path:
    return source_path.relative_to(manuscript_root)


def rewrite_tex_content(
    document_root: Path,
    source_file: Path,
    content: str,
    figure_files: dict[Path, str],
) -> str:
    def replace_graphics(match: re.Match[str]) -> str:
        resolved = resolve_graphics_dependency(document_root, source_file, match.group("path"))
        basename = figure_files.get(resolved)
        if basename is None:
            raise RuntimeError(f"missing staged figure mapping for {resolved}")
        return f"{match.group('prefix')}{{figures/{basename}}}"

    rewritten_lines: list[str] = []
    for line in content.splitlines():
        code, comment = split_code_and_comment(line)
        rewritten_lines.append(GRAPHICS_RE.sub(replace_graphics, code) + comment)
    return "\n".join(rewritten_lines) + ("\n" if content.endswith("\n") else "")


def write_readme(output_root: Path, readme_config: dict[str, object]) -> None:
    lines = [
        f"# {readme_config['title']}",
        "",
        str(readme_config["description"]),
        "",
        f"- Main file: `{readme_config['main_file']}`",
        f"- Compile command: `{readme_config['compile_command']}`",
    ]
    for note in readme_config.get("notes", []):
        lines.append(f"- {note}")
    lines.append("")
    (output_root / "README.md").write_text("\n".join(lines))


def stage_package(
    repo_root: Path,
    manifest: dict[str, object],
    output_root: Path,
) -> tuple[DependencyState, list[Path]]:
    entry_file = (repo_root / str(manifest["entry_file"])).resolve()
    manuscript_root = entry_file.parent.resolve()
    exclude_globs = normalize_globs(manifest.get("exclude_globs", []))
    static_dependencies = [
        (repo_root / str(path)).resolve() for path in manifest.get("static_dependencies", [])
    ]

    state = discover_dependencies(repo_root, entry_file, manuscript_root, exclude_globs)

    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "figures").mkdir(parents=True, exist_ok=True)

    staged_files: list[Path] = []

    for source_file in sorted(state.tex_files):
        relative_target = package_relative_path(manuscript_root, source_file)
        target_path = output_root / relative_target
        target_path.parent.mkdir(parents=True, exist_ok=True)
        rewritten = rewrite_tex_content(
            manuscript_root,
            source_file,
            source_file.read_text(),
            state.figure_files,
        )
        target_path.write_text(rewritten)
        staged_files.append(target_path)

    for source_file in sorted(state.bib_files):
        relative_target = package_relative_path(manuscript_root, source_file)
        target_path = output_root / relative_target
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, target_path)
        staged_files.append(target_path)

    for source_file in static_dependencies:
        relative_repo_path = source_file.relative_to(repo_root)
        if is_excluded(relative_repo_path, exclude_globs):
            raise RuntimeError(f"static dependency matched excluded pattern: {relative_repo_path}")
        relative_target = package_relative_path(manuscript_root, source_file)
        target_path = output_root / relative_target
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, target_path)
        staged_files.append(target_path)

    for source_file, basename in sorted(state.figure_files.items(), key=lambda item: item[1]):
        target_path = output_root / "figures" / basename
        shutil.copy2(source_file, target_path)
        staged_files.append(target_path)

    write_readme(output_root, manifest["readme"])
    staged_files.append(output_root / "README.md")
    return state, staged_files


def verify_staged_package(output_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="cluster-source-verify-") as temp_dir:
        verify_root = Path(temp_dir) / output_root.name
        shutil.copytree(output_root, verify_root)
        result = subprocess.run(
            ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
            cwd=verify_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(
                "clean-dir latexmk verification failed\n"
                f"stdout:\n{result.stdout[-6000:]}\n"
                f"stderr:\n{result.stderr[-6000:]}"
            )


def create_archive(output_root: Path) -> Path:
    archive_path = output_root.with_suffix(".zip")
    if archive_path.exists():
        archive_path.unlink()
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(output_root.rglob("*")):
            if path.is_dir():
                continue
            archive.write(path, arcname=str(path.relative_to(output_root.parent)))
    return archive_path


def main() -> int:
    args = parse_args()
    if not args.verify:
        raise SystemExit("clean-dir verification is mandatory; rerun with --verify")

    manifest_path = args.manifest.resolve()
    repo_root = manifest_path.parents[1]
    manifest = yaml.safe_load(manifest_path.read_text())
    output_root = args.output.resolve()

    state, staged_files = stage_package(repo_root, manifest, output_root)
    verify_staged_package(output_root)

    archive_path: Path | None = None
    if args.archive:
        archive_path = create_archive(output_root)

    print(f"[ok] staged {len(staged_files)} files at {output_root}")
    print(
        "[deps] "
        f"{len(state.tex_files)} tex, "
        f"{len(state.bib_files)} bib, "
        f"{len(state.figure_files)} figures, "
        f"{len(manifest.get('static_dependencies', []))} static extras"
    )
    if state.class_names:
        print(f"[class] {', '.join(sorted(state.class_names))}")
    if archive_path:
        print(f"[archive] {archive_path}")
    print("[verify] clean-dir latexmk passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
