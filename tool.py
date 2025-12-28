import argparse
import winreg
from typing import Optional, List, Set


BASE_PATH = r"SOFTWARE\Native Instruments"


def normalize_path(path: str) -> str:
    """末尾のバックスラッシュを除去"""
    return path.rstrip("\\")


class NativeInstrumentsItem:
    def __init__(self, root, base_path: str, name: str):
        self.root = root
        self.base_path = base_path
        self.name = name

    @property
    def key_path(self) -> str:
        return f"{self.base_path}\\{self.name}"

    def read(self) -> Optional[str]:
        try:
            with winreg.OpenKey(self.root, self.key_path) as key:
                value, _ = winreg.QueryValueEx(key, "ContentDir")
                return value
        except FileNotFoundError:
            return None

    def write(self, new_value: str) -> None:
        with winreg.OpenKey(
            self.root,
            self.key_path,
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            winreg.SetValueEx(
                key,
                "ContentDir",
                0,
                winreg.REG_SZ,
                new_value,
            )

    def __repr__(self) -> str:
        return f"<NIItem {self.name}>"



def enumerate_items_with_content_dir() -> List[NativeInstrumentsItem]:
    items: List[NativeInstrumentsItem] = []

    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, BASE_PATH) as base:
        i = 0
        while True:
            try:
                name = winreg.EnumKey(base, i)
                i += 1

                item = NativeInstrumentsItem(
                    winreg.HKEY_LOCAL_MACHINE,
                    BASE_PATH,
                    name,
                )

                if item.read() is not None:
                    items.append(item)

            except OSError:
                break

    return items


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalize and rewrite Native Instruments ContentDir"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without writing to registry",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="One or more base paths to match against ContentDir",
    )

    args = parser.parse_args()

    # paths を set に格納（正規化もここで）
    target_paths: Set[str] = {normalize_path(p) for p in args.paths}

    items = enumerate_items_with_content_dir()

    for item in items:
        original = item.read()
        if original is None:
            continue

        normalized = normalize_path(original)

        if normalized in target_paths:
            new_value = f"{normalized} Library\\"

            if args.dry_run:
                print(
                    "[DRY-RUN]",
                    item.name,
                    "ContentDir:",
                    repr(original),
                    "->",
                    repr(new_value),
                )
            else:
                item.write(new_value)
                print(
                    "[WRITE]",
                    item.name,
                    "ContentDir:",
                    repr(original),
                    "->",
                    repr(new_value),
                )


if __name__ == "__main__":
    main()
