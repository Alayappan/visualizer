#!/usr/bin/env python3
"""Entry point for Neo4j Graph Visualizer Desktop Application."""
import sys
from pathlib import Path

# Ensure 'src' is in Python module search path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# If running outside the local virtualenv and dependencies are missing, re-exec with .venv
venv_python = root_dir / ".venv" / "bin" / "python"
if venv_python.exists() and sys.executable != str(venv_python.resolve()):
    try:
        import pandas  # noqa: F401
    except ImportError:
        import os
        os.execv(str(venv_python), [str(venv_python)] + sys.argv)

from src.gui.app import main

if __name__ == "__main__":
    main()
