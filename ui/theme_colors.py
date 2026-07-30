"""
Shared color palette — clean, minimal light theme with a blue accent
(matched to assets/icons/app_icon.png's bar color).

Import these instead of hardcoding hex values in individual widgets, so
the whole app stays visually consistent and can be re-themed from one
place later.
"""

NAVY = "#1F2937"           # sidebar/header background — intentionally kept dark
SURFACE = "#FFFFFF"        # dialogs, splash screen
CONTENT_BG = "#F5F6F8"     # main page canvas behind group boxes
ACCENT_BLUE = "#64AAFF"    # icon's bar color — primary accent everywhere
ACCENT_BLUE_DARK = "#4A8AD9"  # slightly darker, for hover/pressed states
BORDER_SUBTLE = "#E2E5EA"  # thin neutral divider on light surfaces
BORDER_SUBTLE_DARK = "#374151"  # thin neutral divider on the dark sidebar/header
NEUTRAL_TRACK = "#CBD5E1"  # unchecked toggle-switch track — needs more contrast than a 1px divider

TEXT_DARK = "#111827"      # primary text on light backgrounds
TEXT_MUTED = "#6B7280"     # muted gray for secondary labels
TEXT_LIGHT = "#E5E7EB"     # light text on the dark sidebar/header
SIDEBAR_SELECTED_TEXT = "#1F2937"  # text for the selected sidebar row, which sits on accent blue

# Semantic status colors — intentionally NOT tied to the accent blue, since
# green/red convey connected/disconnected state and shouldn't be sacrificed
# for brand consistency.
STATUS_OK = "#087F23"
STATUS_ERROR = "#B00020"
STATUS_ERROR_DARK = "#8A0018"  # hover/pressed shade for red danger actions
WARNING_BG = "#FEF3C7"
WARNING_BORDER = "#F59E0B"
WARNING_TEXT = "#92400E"

# Direction accents — TX and RX need to read as visually distinct at a
# glance (chart legend, Data Sending/Receiving cards), not just labeled
# the same way.
TX_ACCENT = ACCENT_BLUE
RX_ACCENT = "#10B981"  # emerald — distinct from STATUS_OK so it reads as "receiving," not "success"

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

# Applied app-wide via QApplication.setStyleSheet. Cards are a custom
# Card widget (ui/widgets/card.py), not QGroupBox — Qt's native QGroupBox
# always renders its title cut into the border line no matter what QSS
# is layered on top, so it's not used anywhere in this app anymore.
# PrimaryButton marks the one main action per section (Connect, Apply,
# Save, Set) with a filled accent-blue treatment; everything else stays
# a plain secondary button, so the UI has an actual visual hierarchy
# instead of every control looking equally important.
GLOBAL_QSS = f"""
QChartView {{
    background: #FFFFFF;
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 8px;
}}
QPushButton {{
    background: #FFFFFF;
    color: {TEXT_DARK};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 5px;
    padding: 4px 10px;
}}
QPushButton:hover {{
    border-color: {ACCENT_BLUE};
}}
QPushButton:pressed {{
    background: {CONTENT_BG};
}}
QPushButton#PrimaryButton {{
    background: {ACCENT_BLUE};
    color: #FFFFFF;
    border: none;
    font-weight: 600;
}}
QPushButton#PrimaryButton:hover {{
    background: {ACCENT_BLUE_DARK};
}}
QPushButton#PrimaryButton:pressed {{
    background: {ACCENT_BLUE_DARK};
}}
QComboBox, QLineEdit, QSpinBox {{
    background: #FFFFFF;
    color: {TEXT_DARK};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 5px;
    padding: 2px 6px;
}}
QComboBox:focus, QLineEdit:focus, QSpinBox:focus {{
    border-color: {ACCENT_BLUE};
}}
QComboBox QAbstractItemView {{
    background: #FFFFFF;
    color: {TEXT_DARK};
    border: 1px solid {BORDER_SUBTLE};
    outline: 0;
    selection-background-color: {ACCENT_BLUE};
    selection-color: #FFFFFF;
}}
QLineEdit:read-only {{
    background: {CONTENT_BG};
    color: {TEXT_MUTED};
}}
"""


def card_shadow():
    """A subtle drop shadow for Card widgets, giving them real elevation
    off the page canvas instead of just a flat outline. Call per-instance:
    widget.setGraphicsEffect(card_shadow())."""
    from PySide6.QtWidgets import QGraphicsDropShadowEffect
    from PySide6.QtGui import QColor

    effect = QGraphicsDropShadowEffect()
    effect.setBlurRadius(12)
    effect.setOffset(0, 2)
    effect.setColor(QColor(17, 24, 39, 30))  # TEXT_DARK at low alpha
    return effect


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