"""Theme configuration and visual styles for Tkinter GUI."""
import tkinter as tk
from tkinter import ttk

# Modern Dark-Slate Palette
BG_DARK = "#0f172a"          # Slate 900
BG_PANEL = "#1e293b"         # Slate 800
BG_CARD = "#334155"          # Slate 700
BG_HOVER = "#475569"         # Slate 600

TEXT_PRIMARY = "#f8fafc"     # Slate 50
TEXT_SECONDARY = "#94a3b8"   # Slate 400
TEXT_MUTED = "#64748b"       # Slate 500

ACCENT_BLUE = "#3b82f6"      # Blue 500
ACCENT_BLUE_HOVER = "#2563eb"# Blue 600
ACCENT_CYAN = "#06b6d4"      # Cyan 500

SUCCESS_GREEN = "#10b981"    # Emerald 500
SUCCESS_BG = "#064e3b"       # Emerald 900
ERROR_RED = "#ef4444"        # Red 500
ERROR_BG = "#7f1d1d"         # Red 900
WARNING_AMBER = "#f59e0b"    # Amber 500

# Graph Visual Elements
CANVAS_BG = "#0b1120"        # Very dark blue-gray
GRID_COLOR = "#1e293b"

NODE_FILL = "#3b82f6"
NODE_OUTLINE = "#60a5fa"
NODE_TEXT = "#ffffff"
NODE_RADIUS = 24

NODE_SELECTED_FILL = "#f59e0b"
NODE_SELECTED_OUTLINE = "#fde68a"

NODE_SHADOW = "#040814"
NODE_SPECULAR = "#93c5fd"
NODE_SELECTED_SPECULAR = "#fef08a"

EDGE_COLOR = "#64748b"
EDGE_HOVER_COLOR = "#94a3b8"
EDGE_SELECTED_COLOR = "#f59e0b"
EDGE_TEXT = "#cbd5e1"
EDGE_TEXT_BG = "#1e293b"


def apply_theme(root: tk.Tk) -> ttk.Style:
    """Apply modern dark styling to ttk widgets."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    root.configure(bg=BG_DARK)

    # General Frame
    style.configure("TFrame", background=BG_DARK)
    style.configure("Panel.TFrame", background=BG_PANEL)
    style.configure("Card.TFrame", background=BG_CARD)

    # Label styling
    style.configure("TLabel", background=BG_DARK, foreground=TEXT_PRIMARY, font=("Helvetica", 11))
    style.configure("Panel.TLabel", background=BG_PANEL, foreground=TEXT_PRIMARY, font=("Helvetica", 11))
    style.configure("Header.TLabel", background=BG_DARK, foreground=TEXT_PRIMARY, font=("Helvetica", 16, "bold"))
    style.configure("Subheader.TLabel", background=BG_DARK, foreground=TEXT_SECONDARY, font=("Helvetica", 12))
    style.configure("CardHeader.TLabel", background=BG_CARD, foreground=TEXT_PRIMARY, font=("Helvetica", 12, "bold"))
    style.configure("Secondary.TLabel", background=BG_PANEL, foreground=TEXT_SECONDARY, font=("Helvetica", 10))

    # Buttons
    style.configure(
        "TButton",
        background=BG_CARD,
        foreground=TEXT_PRIMARY,
        borderwidth=0,
        focusthickness=0,
        padding=(12, 8),
        font=("Helvetica", 11, "bold"),
    )
    style.map(
        "TButton",
        background=[("active", BG_HOVER), ("disabled", BG_PANEL)],
        foreground=[("disabled", TEXT_MUTED)],
    )

    style.configure(
        "Primary.TButton",
        background=ACCENT_BLUE,
        foreground="#ffffff",
        borderwidth=0,
        focusthickness=0,
        padding=(14, 8),
        font=("Helvetica", 11, "bold"),
    )
    style.map(
        "Primary.TButton",
        background=[("active", ACCENT_BLUE_HOVER), ("disabled", BG_CARD)],
        foreground=[("disabled", TEXT_MUTED)],
    )

    style.configure(
        "Success.TButton",
        background=SUCCESS_GREEN,
        foreground="#ffffff",
        borderwidth=0,
        padding=(14, 8),
        font=("Helvetica", 11, "bold"),
    )

    # Entry
    style.configure(
        "TEntry",
        fieldbackground=BG_PANEL,
        foreground=TEXT_PRIMARY,
        insertcolor=TEXT_PRIMARY,
        padding=6,
        font=("Helvetica", 11),
    )

    # Treeview (for properties table)
    style.configure(
        "Treeview",
        background=BG_PANEL,
        foreground=TEXT_PRIMARY,
        fieldbackground=BG_PANEL,
        font=("Helvetica", 10),
        rowheight=24,
    )
    style.configure(
        "Treeview.Heading",
        background=BG_CARD,
        foreground=TEXT_PRIMARY,
        font=("Helvetica", 10, "bold"),
    )
    style.map("Treeview", background=[("selected", ACCENT_BLUE)])

    # Scrollbars
    style.configure(
        "Vertical.TScrollbar",
        background=BG_CARD,
        troughcolor=BG_PANEL,
        arrowcolor=TEXT_PRIMARY,
        borderwidth=0,
    )

    return style
