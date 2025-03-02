from ..utils.module_loader import load_modules_from_directory
import os
import glob
import importlib
from .server_service import add_server, remove_server, list_servers

current_dir = os.path.dirname(__file__)
modules = load_modules_from_directory(current_dir, __package__)

__all__ = []
for module in modules:
    if hasattr(module, "__all__"):
        __all__.extend(module.__all__)
    else:
        __all__.extend([attr for attr in dir(module) if not attr.startswith("_")])