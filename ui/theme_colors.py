"""
Shared color palette — clean, minimal light theme with a blue accent
(matched to assets/icons/app_icon.png's bar color).

Import these instead of hardcoding hex values in individual widgets, so
the whole app stays visually consistent and can be re-themed from one
place later.
"""

SURFACE = "#FFFFFF"        # sidebar, header, dialogs, splash screen
CONTENT_BG = "#F5F6F8"     # main page canvas behind group boxes
ACCENT_BLUE = "#64AAFF"    # icon's bar color — primary accent everywhere
ACCENT_BLUE_DARK = "#4A8AD9"  # slightly darker, for hover/pressed states
BORDER_SUBTLE = "#E2E5EA"  # thin neutral divider — sidebar/content split, header bottom line
NEUTRAL_TRACK = "#CBD5E1"  # unchecked toggle-switch track — needs more contrast than a 1px divider

TEXT_DARK = "#111827"      # primary text on light backgrounds
TEXT_MUTED = "#6B7280"     # muted gray for secondary labels
SIDEBAR_SELECTED_TEXT = "#1F2937"  # text for the selected sidebar row, which sits on accent blue

# Kept only for status_card.py/section_card.py, which are unused by any
# page (see HANDOFF_GUIDE.md) but still imported by ui/widgets/__init__.py
# at startup — removing this would break the app on launch even though
# the widgets themselves are dead code.
TEXT_LIGHT = "#E5E7EB"

# Semantic status colors — intentionally NOT tied to the accent blue, since
# green/red convey connected/disconnected state and shouldn't be sacrificed
# for brand consistency.
STATUS_OK = "#087F23"
STATUS_ERROR = "#B00020"
STATUS_ERROR_DARK = "#8A0018"  # hover/pressed shade for the red logout circle
WARNING_BG = "#FEF3C7"
WARNING_BORDER = "#F59E0B"
WARNING_TEXT = "#92400E"

# Dialog surface — plain white panel with a subtle border/shadow so a
# modal reads as "on top of" the app rather than blending into it.
DIALOG_BG = "#FFFFFF"

# Full QRadioButton stylesheet including the indicator (circle) explicitly.
# Any QSS on a QRadioButton switches it off native rendering for whatever
# you didn't specify — if you only set color/background, the checked
# state's indicator dot can render blank. Always use this full style,
# not just a color override, whenever a radio button needs custom colors.
RADIO_BUTTON_STYLE = f"""
QRadioButton {{ color: {TEXT_DARK}; background: transparent; }}
QRadioButton::indicator {{
    width: 14px; height: 14px; border-radius: 7px;
    border: 2px solid {BORDER_SUBTLE}; background: transparent;
}}
QRadioButton::indicator:checked {{
    border: 2px solid {ACCENT_BLUE}; background: {ACCENT_BLUE};
}}
"""


def light_palette():
    """A single, non-switchable light QPalette — forces a clean white/light
    look regardless of the OS's dark/light mode setting, using Fusion
    style (the only style that reliably respects QPalette everywhere)."""
    from PySide6.QtGui import QPalette, QColor

    p = QPalette()
    p.setColor(QPalette.Window, QColor(CONTENT_BG))
    p.setColor(QPalette.WindowText, QColor(TEXT_DARK))
    p.setColor(QPalette.Base, QColor("#FFFFFF"))
    p.setColor(QPalette.AlternateBase, QColor(CONTENT_BG))
    p.setColor(QPalette.ToolTipBase, QColor("#FFFFFF"))
    p.setColor(QPalette.ToolTipText, QColor(TEXT_DARK))
    p.setColor(QPalette.Text, QColor(TEXT_DARK))
    p.setColor(QPalette.Button, QColor("#FFFFFF"))
    p.setColor(QPalette.ButtonText, QColor(TEXT_DARK))
    p.setColor(QPalette.BrightText, QColor(STATUS_ERROR))
    p.setColor(QPalette.Link, QColor(ACCENT_BLUE))
    p.setColor(QPalette.Highlight, QColor(ACCENT_BLUE))
    p.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    p.setColor(QPalette.Disabled, QPalette.Text, QColor(TEXT_MUTED))
    p.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(TEXT_MUTED))
    return p
