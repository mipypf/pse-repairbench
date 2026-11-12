#!/usr/bin/env python3
"""Remove local absolute workspace paths from tracked benchmark artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


TEXT_SUFFIXES = {".csv", ".html", ".md", ".txt"}
JSON_SUFFIXES = {".json"}
DEFAULT_ROOTS = [Path("instances"), Path("metadata/dwsim_sources"), Path("docs/dwsim")]
LOCAL_PATH_PATTERNS = [
    re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+"),
    re.compile(r"[A-Za-z]:\\\\Users\\\\"),
    re.compile(r"(?:^|[\"'])\.tmp[\\/]final_v0_1_5[\\/]"),
]


def repo_root() -> Path:
    return Path.cwd().resolve()


def sanitize_json(path: Path, check: bool) -> bool:
    original = path.read_text(encoding="utf-8-sig")
    output = replace_unstable_paths(original, path)
    # Ensure JSON files remain valid after text-level path replacement.
    json.loads(output)
    changed = output != original
    if changed and not check:
        path.write_text(output, encoding="utf-8")
    return changed


def replacement_pairs() -> list[tuple[str, str]]:
    root = repo_root()
    home = Path.home()
    win = str(root)
    posix = root.as_posix()
    home_win = str(home)
    home_posix = home.as_posix()
    local_appdata_win = str(home / "AppData" / "Local")
    local_appdata_posix = (home / "AppData" / "Local").as_posix()
    json_escaped_win = json.dumps(win, ensure_ascii=True)[1:-1]
    json_escaped_posix = json.dumps(posix, ensure_ascii=True)[1:-1]
    return [
        (win + "\\", ""),
        (win + "/", ""),
        (win.replace("\\", "\\\\") + "\\\\", ""),
        (json_escaped_win + "\\\\", ""),
        (posix + "/", ""),
        (json_escaped_posix + "/", ""),
        (win, "."),
        (win.replace("\\", "\\\\"), "."),
        (json_escaped_win, "."),
        (posix, "."),
        (json_escaped_posix, "."),
        (local_appdata_win + "\\", "%LOCALAPPDATA%/"),
        (local_appdata_win.replace("\\", "\\\\") + "\\\\", "%LOCALAPPDATA%/"),
        (local_appdata_posix + "/", "%LOCALAPPDATA%/"),
        (home_win + "\\", "%USERPROFILE%/"),
        (home_win.replace("\\", "\\\\") + "\\\\", "%USERPROFILE%/"),
        (home_posix + "/", "%USERPROFILE%/"),
    ]


def bytes_replacement_pairs() -> list[tuple[bytes, bytes]]:
    pairs: list[tuple[bytes, bytes]] = []
    for needle, replacement in replacement_pairs():
        for encoding in ("utf-8", "cp932"):
            try:
                pairs.append((needle.encode(encoding), replacement.encode("ascii")))
            except UnicodeEncodeError:
                continue
    return pairs


def instance_id_from_path(path: Path) -> str | None:
    parts = path.parts
    try:
        index = parts.index("candidate_pool")
    except ValueError:
        return None
    if index + 1 < len(parts):
        return parts[index + 1]
    return None


def replace_unstable_paths(text: str, path: Path) -> str:
    output = text
    for needle, replacement in replacement_pairs():
        output = output.replace(needle, replacement)
    instance_id = instance_id_from_path(path)
    if instance_id:
        for slash in ("/", "\\\\"):
            output = output.replace(
                f".tmp{slash}final_v0_1_5{slash}candidate_pool_thermocs_rescued_mps4{slash}{instance_id}{slash}",
                "",
            )
    output = output.replace(".tmp/final_v0_1_5/", "local_generation_artifacts/final_v0_1_5/")
    output = output.replace(".tmp\\\\final_v0_1_5\\\\", "local_generation_artifacts\\\\final_v0_1_5\\\\")
    return output


def sanitize_text(path: Path, check: bool) -> bool:
    try:
        original = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        raw = path.read_bytes()
        output = raw
        for needle, replacement in bytes_replacement_pairs():
            output = output.replace(needle, replacement)
        changed = output != raw
        if changed and not check:
            path.write_bytes(output)
        return changed
    output = replace_unstable_paths(original, path)
    changed = output != original
    if changed and not check:
        path.write_text(output, encoding="utf-8")
    return changed


def iter_files(roots: list[Path]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
        elif root.exists():
            files.extend(path for path in root.rglob("*") if path.is_file())
    return sorted(files)


def contains_local_path(path: Path) -> bool:
    raw = path.read_bytes()
    if b"C:\\Users\\" in raw or b"C:/Users/" in raw or b".tmp/final_v0_1_5/" in raw or b".tmp\\final_v0_1_5\\" in raw:
        return True
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return False
    return any(pattern.search(text) for pattern in LOCAL_PATH_PATTERNS)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, default=DEFAULT_ROOTS)
    parser.add_argument("--check", action="store_true", help="fail if any file would be changed or still contains a local path")
    args = parser.parse_args()

    changed: list[Path] = []
    unsupported_with_paths: list[Path] = []
    for path in iter_files(args.paths):
        if path.suffix.lower() in JSON_SUFFIXES:
            if sanitize_json(path, args.check):
                changed.append(path)
        elif path.suffix.lower() in TEXT_SUFFIXES:
            if sanitize_text(path, args.check):
                changed.append(path)
        elif contains_local_path(path):
            unsupported_with_paths.append(path)

    remaining = [path for path in iter_files(args.paths) if contains_local_path(path)]
    for path in changed:
        print(f"changed: {path}")
    for path in unsupported_with_paths:
        print(f"unsupported file still contains local path: {path}", file=sys.stderr)
    for path in remaining:
        print(f"local path remains: {path}", file=sys.stderr)

    if args.check and (changed or remaining or unsupported_with_paths):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
