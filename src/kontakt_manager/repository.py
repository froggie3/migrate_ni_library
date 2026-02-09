import winreg
import logging
from typing import Optional
from .core import Library

logger = logging.getLogger(__name__)


class LibraryRepository:
    """Handles persistence of Kontakt library states via Windows Registry."""

    HKLM_PATH = r"SOFTWARE\Native Instruments"
    HKCU_PATH = r"Software\Native Instruments"

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        if self.dry_run:
            logger.info("dry run enabled: no changes will be written")

    def fetch_all(self) -> list[Library]:
        """scans the registry for Kontakt libraries."""
        libraries = []

        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.HKLM_PATH) as root_key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(root_key, i)
                        lib = self._load_library(subkey_name)
                        if lib:
                            libraries.append(lib)
                        i += 1
                    except OSError:
                        break  # End of keys
        except OSError as e:
            logger.error(f"Failed to access HKLM registry: {e}")

        return libraries

    def _load_library(self, id: str) -> Optional[Library]:
        """Loads a single library's data, verifying it's a Kontakt library."""
        hklm_subpath = f"{self.HKLM_PATH}\\{id}"
        hkcu_subpath = f"{self.HKCU_PATH}\\{id}"

        try:
            # 1. Check HKLM for ContentDir and Visibility (Validation Heuristic)
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, hklm_subpath) as key:
                try:
                    content_dir, _ = winreg.QueryValueEx(key, "ContentDir")
                except FileNotFoundError:
                    return None  # Not a library (e.g. effect plugin)

                try:
                    # Kontakt libraries usually have a Visibility key
                    winreg.QueryValueEx(key, "Visibility")
                except FileNotFoundError:
                    # Could be an expansion or other NI product
                    # We only care about Kontakt Libraries for this scope
                    return None

            # 2. Check HKCU for UserRemoved status
            is_visible = True
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, hkcu_subpath) as key:
                    try:
                        user_removed, _ = winreg.QueryValueEx(key, "UserRemoved")
                        if user_removed == 1:
                            is_visible = False
                    except FileNotFoundError:
                        pass  # Default to visible
            except FileNotFoundError:
                pass  # Key doesn't exist in HKCU yet

            return Library(
                id=id,
                name=id,  # Subkey name is usually the product name
                install_path=content_dir,
                is_visible=is_visible,
            )

        except OSError:
            return None

    def set_visibility(self, library_id: str, visible: bool):
        """Toggles the visibility of a library by setting/removing UserRemoved in HKCU."""
        hkcu_subpath = f"{self.HKCU_PATH}\\{library_id}"

        action = "show" if visible else "hide"
        logger.info(f"{action} {library_id}")

        if self.dry_run:
            return

        try:
            # Open or Create the HKCU key for this library
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, hkcu_subpath) as key:
                if not visible:
                    # hide: set UserRemoved = 1
                    winreg.SetValueEx(key, "UserRemoved", 0, winreg.REG_DWORD, 1)
                    logger.debug(f"set UserRemoved=1 for {library_id}")
                else:
                    # show: remove UserRemoved value
                    try:
                        winreg.DeleteValue(key, "UserRemoved")
                        logger.debug(f"deleted UserRemoved for {library_id}")
                    except FileNotFoundError:
                        pass  # already visible
        except OSError as e:
            logger.error(f"failed to update registry for {library_id}: {e}")
            raise
