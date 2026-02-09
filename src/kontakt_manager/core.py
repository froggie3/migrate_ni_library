from dataclasses import dataclass


@dataclass
class Library:
    """Represents a Kontakt library and its system state."""

    id: str  # The registry key name (e.g., "Alicia's Keys")
    name: str  # Display name
    install_path: str  # ContentDir path
    is_visible: bool  # Computed visibility state (True if not 'UserRemoved')

    @property
    def humancase_name(self) -> str:
        """Standardized name for easier search/matching."""
        return self.name.lower().strip()

    def __repr__(self) -> str:
        status = "Visible" if self.is_visible else "Hidden"
        return (
            f"Library(name='{self.name}', status={status}, path='{self.install_path}')"
        )
