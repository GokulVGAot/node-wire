from __future__ import annotations

from abc import ABC, abstractmethod


class SecretProvider(ABC):
    """
    Abstract port for secret resolution.

    Implementations live in Layer C and may use environment variables,
    a secrets manager, or any other secure storage.
    """

    @abstractmethod
    def get_secret(self, key: str) -> str:
        """Return the secret value for the given key or raise an exception."""
        raise NotImplementedError
