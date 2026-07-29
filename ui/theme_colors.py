"""
Shared color palette, matched to assets/icons/app_icon.png:
dark navy background + blue accent bars.

Import these instead of hardcoding hex values in individual widgets, so
the whole app stays visually tied to the icon and can be re-themed from
one place later.
"""

NAVY = "#1F2937"          # icon background — used by the sidebar
ACCENT_BLUE = "#64AAFF"   # icon's bar color — primary accent everywhere else
ACCENT_BLUE_DARK = "#4A8AD9"  # slightly darker, for hover/pressed states
BORDER_SUBTLE = "#4B5563"  # thin neutral divider — sidebar/content split, header bottom line

TEXT_LIGHT = "#E5E7EB"    # light text on dark backgrounds (sidebar)
TEXT_MUTED = "#6B7280"    # muted gray for secondary labels
TEXT_DARK = "#111827"     # dark text on light backgrounds

# Semantic status colors — intentionally NOT tied to the accent blue, since
# green/red convey connected/disconnected state and shouldn't be sacrificed
# for brand consistency.
STATUS_OK = "#087F23"
STATUS_ERROR = "#B00020"
STATUS_ERROR_DARK = "#8A0018"  # hover/pressed shade for the red logout circle
WARNING_BG = "#FEF3C7"
WARNING_BORDER = "#F59E0B"
WARNING_TEXT = "#92400E"

# Dialog surface — one shade lighter than the sidebar navy so a modal
# reads as "on top of" the app rather than blending into it.
DIALOG_BG = "#242F3F"

# Full QRadioButton stylesheet including the indicator (circle) explicitly.
# Any QSS on a QRadioButton switches it off native rendering for whatever
# you didn't specify — if you only set color/background, the checked
# state's indicator dot can render blank. Always use this full style,
# not just a color override, whenever a radio button needs a light color
# on a dark background.
RADIO_BUTTON_STYLE = f"""
QRadioButton {{ color: {TEXT_LIGHT}; background: transparent; }}
QRadioButton::indicator {{
    width: 14px; height: 14px; border-radius: 7px;
    border: 2px solid {BORDER_SUBTLE}; background: transparent;
}}
QRadioButton::indicator:checked {{
    border: 2px solid {ACCENT_BLUE}; background: {ACCENT_BLUE};
}}
"""
