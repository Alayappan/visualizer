---
name: desktop-app-workflow
description: Use when building, enhancing, or debugging Tkinter desktop application UI flows, view transitions, menus, toolbar commands, keyboard shortcuts, and inspector drawers.
---

# Desktop App Workflow Skill

## 1. Overview & Purpose
This skill governs the Tkinter desktop application architecture, view transitions, state management, and user interaction flows in [`src/gui/`](file:///Users/kamalesh/Downloads/neo4j-visualizer/visualizer/src/gui/).

---

## 2. Desktop State Lifecycle

The application operates as a deterministic state machine:

```text
[1. File Selection View]
  - Displays file paths for nodes.csv and relations.csv.
  - "Browse..." opens native OS file pickers.
  - "Sample Data" loads included test fixtures.
  - "Validate CSV Files" triggers CSVValidator.

[2. Validation Results]
  ├─ If Errors:
  │    - Displays error banner with count.
  │    - Lists all failing rows and column reasons in scrollable text box.
  │    - Keeps file inputs editable for correction.
  └─ If Valid:
       - Displays green success banner with node & relation counts.
       - Enables "Visualize Graph" button.

[3. Graph Workspace View]
  - Triggered by "Visualize Graph".
  - Hides file selection view; displays paned workspace:
    - Center: Interactive GraphCanvas.
    - Right: DetailPanel inspector drawer.
  - Enables toolbar tools: Zoom In, Zoom Out, Fit Screen, Re-layout, New Upload.
  - Updates bottom status bar with counts and zoom percentage.

[4. Inspector Drawer]
  - Clicking any node or relationship displays attributes in DetailPanel.
  - Shows formatted JSON properties in a ttk.Treeview table.
  - "Close" button clears selection without losing viewport zoom/pan.

[5. Reset / New Upload]
  - "New Upload" returns to File Selection View.
```

---

## 3. Keyboard Shortcuts & Native Controls

- `Ctrl/Cmd + O`: Open file upload view
- `Ctrl/Cmd + +`: Zoom In
- `Ctrl/Cmd + -`: Zoom Out
- `Ctrl/Cmd + 0`: Fit Graph to Screen
- `Escape`: Clear selection / dismiss detail panel
- `Ctrl/Cmd + Q`: Exit application

---

## 4. Verification & Testing

Run all GUI unit tests:
```bash
pytest tests/test_gui.py -v
```
All GUI components run headlessly in tests via `root.withdraw()`.
