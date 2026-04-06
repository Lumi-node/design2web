"""Pytest configuration for tests.

This module configures pytest to properly import the project's types module,
which has the same name as Python's stdlib types module.
"""

import sys
import importlib.util
from pathlib import Path
import builtins

# Load types.py explicitly by file path to avoid conflict with stdlib types
project_root = Path(__file__).parent.parent
types_path = project_root / "types.py"

# Load the types module with a unique name in sys.modules
spec = importlib.util.spec_from_file_location("project_types", str(types_path))
project_types = importlib.util.module_from_spec(spec)
sys.modules['project_types'] = project_types
spec.loader.exec_module(project_types)
