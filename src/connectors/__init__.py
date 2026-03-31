from __future__ import annotations

"""
Node Wire - Layer B: System Adapters.

Each connector lives in its own subpackage and follows the three-file pattern:

    connector_name/
      schema.py
      logic.py
      registration.py

Registration modules are auto-discovered so they can register system-specific
exceptions with the global ErrorMapper in Layer A.
"""

from importlib import import_module
from pkgutil import iter_modules
from typing import Iterable, List


def auto_register() -> List[str]:
    """
    Import all `registration` modules in connector subpackages.

    Returns the list of successfully imported module names. This should be
    called once at process startup (e.g. by Layer C bindings) to ensure all
    connector-specific error mappings are registered.
    """
    imported: List[str] = []
    package_name = __name__

    for module_info in iter_modules(__path__, prefix=f"{package_name}."):
        # We only care about subpackages; each is expected to expose registration.py
        if not module_info.ispkg:
            continue

        registration_module = f"{module_info.name}.registration"
        try:
            import_module(registration_module)
            imported.append(registration_module)
        except ModuleNotFoundError:
            # Connector without a registration module; skip silently.
            continue

    return imported


__all__ = ["auto_register"]

