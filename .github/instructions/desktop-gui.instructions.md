---
applyTo: "src/gui/**"
description: "Desktop GUI coding standards for the Python Tkinter application, Canvas rendering, and UI components."
---

# Desktop GUI Instructions

## Scope
Apply these instructions when working on desktop GUI files under `src/gui/`.

## Stack and Conventions
- Use Python 3.10+ and Tkinter/TTK.
- Use `src/gui/theme.py` for all color constants and style definitions.
- Keep components modular: `FileSelector`, `GraphCanvas`, `DetailPanel`, and `GraphVisualizerApp`.
- Maintain clean event handling and avoid blocking the main UI thread.
- Ensure all GUI widgets are headlessly testable via `root.withdraw()` in pytest.
