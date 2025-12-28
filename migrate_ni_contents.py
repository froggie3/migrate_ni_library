from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


# =========================
# Domain Model
# =========================

@dataclass
class ContentDir:
    name: str
    path: Path
    related: List["ContentDir"] = field(default_factory=list)

    def link(self, other: "ContentDir") -> None:
        if other is self:
            return
        if other not in self.related:
            self.related.append(other)
        if self not in other.related:
            other.related.append(self)

    @property
    def has_library_suffix(self) -> bool:
        return self.name.endswith(" Library")


# =========================
# Utilities
# =========================

LIBRARY_SUFFIX = " Library"


def normalize_name(name: str) -> str:
    if name.endswith(LIBRARY_SUFFIX):
        return name[: -len(LIBRARY_SUFFIX)]
    return name


def load_directories(root: Path) -> List[ContentDir]:
    return [
        ContentDir(name=p.name, path=p)
        for p in root.iterdir()
        if p.is_dir()
    ]


def find_pairs(dirs: List[ContentDir]) -> None:
    by_normalized: Dict[str, List[ContentDir]] = {}

    for d in dirs:
        key = normalize_name(d.name)
        by_normalized.setdefault(key, []).append(d)

    for group in by_normalized.values():
        if len(group) < 2:
            continue
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                group[i].link(group[j])


# =========================
# Commands
# =========================

def cmd_move(root: Path, backup: Path, dry_run: bool) -> None:
    dirs = load_directories(root)

    targets = [d for d in dirs if d.has_library_suffix]

    if dry_run:
        for d in targets:
            print(f"[DRY-RUN] move: {d.path}")
        return

    backup.mkdir(parents=True, exist_ok=True)

    for d in targets:
        dest = backup / d.name
        print(f"move: {d.path} -> {dest}")
        shutil.move(str(d.path), str(dest))


def cmd_rename(paths: List[Path], dry_run: bool) -> None:
    for p in paths:
        if not p.exists() or not p.is_dir():
            continue

        if p.name.endswith(LIBRARY_SUFFIX):
            continue

        new_name = p.name + LIBRARY_SUFFIX
        new_path = p.with_name(new_name)

        if dry_run:
            print(f"[DRY-RUN] rename: {p} -> {new_path}")
            continue

        print(f"rename: {p} -> {new_path}")
        p.rename(new_path)


# =========================
# CLI
# =========================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="NI Contents directory maintenance tool"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # move
    move_parser = subparsers.add_parser("move", help="move * Library dirs to backup")
    move_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show targets without moving",
    )

    # rename
    rename_parser = subparsers.add_parser(
        "rename", help="remove trailing ' Library' from directory names"
    )
    rename_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show rename targets without renaming",
    )
    rename_parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="one or more directory paths",
    )

    return parser


def main() -> None:
    root = Path(r"C:\mnt2\#Composing\libraries\NI_Contents")
    backup = Path(r"C:\mnt2\#Composing\libraries\NI_Contents.bak")

    parser = build_parser()
    args = parser.parse_args()

    if args.command == "move":
        cmd_move(root=root, backup=backup, dry_run=args.dry_run)

    elif args.command == "rename":
        cmd_rename(paths=args.paths, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
