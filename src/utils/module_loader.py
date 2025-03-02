import os
import glob
import importlib

def load_modules_from_directory(directory, package):
    module_files = glob.glob(os.path.join(directory, "*.py"))
    modules = []
    
    for module_path in module_files:
        if module_path.endswith("__init__.py"):
            continue
        
        module_name = os.path.basename(module_path)[:-3]
        module = importlib.import_module(f".{module_name}", package=package)
        modules.append(module)
    
    return modules
