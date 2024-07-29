from __future__ import annotations

import importlib
import pkgutil


def scan_modules(root_package_name: str):
    """Import all modules in a package (recursively), for side effects."""
    for module_name in iter_module_names(root_package_name):
        _module = importlib.import_module(module_name)


def iter_module_names(package_name: str):
    package = importlib.import_module(package_name)
    path = package.__path__
    prefix = package.__name__ + "."
    for _, module_name, is_pkg in pkgutil.walk_packages(path, prefix):
        if not is_pkg:
            yield module_name
