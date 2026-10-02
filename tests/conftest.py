"""Pytest configuration for desktop visualizer tests."""
import sys
from pathlib import Path
from unittest.mock import MagicMock
import pytest

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@pytest.fixture(autouse=True)
def mock_messagebox(monkeypatch):
    """Prevent blocking modal dialogs during automated test runs."""
    import tkinter.messagebox
    monkeypatch.setattr(tkinter.messagebox, "showinfo", MagicMock(return_value="ok"))
    monkeypatch.setattr(tkinter.messagebox, "showerror", MagicMock(return_value="ok"))
    monkeypatch.setattr(tkinter.messagebox, "showwarning", MagicMock(return_value="ok"))
    monkeypatch.setattr(tkinter.messagebox, "askyesno", MagicMock(return_value=True))
    monkeypatch.setattr(tkinter.messagebox, "askokcancel", MagicMock(return_value=True))
