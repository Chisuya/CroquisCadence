"""
Theme configuration for CroquisCadence
"""

THEMES = {
    "studio": {
        "name": "Studio",
        "dark": "#1a1a1a",         # Very dark gray (background)
        "gray": "#2a2a2a",         # Medium dark gray (controls bar)
        "light_gray": "#3a3a3a",   # Light dark gray (containers)
        "primary": "#4a6fa5",      # Blue (active/selected buttons - from screenshot)
        "secondary": "#e8e8e8",    # Light gray/white (inactive buttons - from screenshot)
        "accent": "#5a7fb5",       # Lighter blue (hover state)
        "success": "#4a6fa5",      # Blue for success
        "text": "#ffffff",         # White text (for blue buttons)
        "text_secondary": "#000000",  # BLACK text for light gray buttons
        "warning": "#ffffff",      # White for warnings
        "timer": "#ffffff",        # White timer
        # Warning colors for timer
        "timer_normal": "#ffffff",     # White
        "timer_warning_50": "#e8e8e8",  # Light gray
        "timer_warning_10": "#4a6fa5",  # Blue (stands out!)
        # Canvas background - neutral 50% gray
        "canvas_bg": "#808080",    # 50% gray (neutral, no color cast)
    },
    "cyberpunk": {
        "name": "Cyberpunk",
        "dark": "#0f0f0f",
        "gray": "#1f1f1f",
        "light_gray": "#2a2a2a",
        "primary": "#FF6EC7",      # Pink
        "secondary": "#67E8F9",    # Blue
        "accent": "#8B5CF6",       # Purple
        "success": "#67F971",      # Green
        "text": "#E5E5E5",
        "text_secondary": "#000000",  # Black text for light buttons
        "warning": "#FF6EC7",      # Pink for warnings
        "timer": "#FF6EC7",        # Pink for timer (same as primary)
        # Warning colors for timer
        "timer_normal": "#FF6EC7",     # Normal time (pink)
        "timer_warning_50": "#FF8DD7",  # 50% warning (lighter pink)
        "timer_warning_10": "#FF3399",  # 10% warning (hot pink)
        # Canvas background
        "canvas_bg": "#808080",    # 50% gray (neutral, no color cast)
    },
    "matcha": {
        "name": "Matcha Latte",
        "dark": "#1a1d1a",         # Very dark warm gray (almost black with green hint)
        "gray": "#252b25",         # Dark warm gray (frames)
        "light_gray": "#303630",   # Medium dark gray (containers)
        "primary": "#88b04b",      # Vibrant matcha green (main buttons)
        "secondary": "#a8d08d",    # Light fresh green (accents)
        "accent": "#6b8e23",       # Rich olive green (secondary buttons)
        "success": "#9db07e",      # Soft sage green (success states)
        "text": "#e8f5e9",
        "text_secondary": "#000000",  # Black text for light buttons         # Very light cream (text on dark)
        "warning": "#ff6b35",      # BRIGHT saturated orange-red (WARNING timer - impossible to miss!)
        "timer": "#d4a574",        # Warm tan/cream (NORMAL timer - pops on dark!)
        # Warning colors for timer
        "timer_normal": "#d4a574",     # Normal time (warm tan)
        "timer_warning_50": "#e8a87c",  # 50% warning (peachy tan)
        "timer_warning_10": "#ff6b35",  # 10% warning (bright orange)
        # Canvas background
        "canvas_bg": "#808080",    # 50% gray (neutral, no color cast)
    }
}

def get_theme(theme_name: str = "studio") -> dict:
    """Get theme colors by name"""
    # Check custom themes first
    custom_themes = load_custom_themes()
    if theme_name in custom_themes:
        return custom_themes[theme_name]
    return THEMES.get(theme_name, THEMES["studio"])

def load_current_theme() -> str:
    """Load saved theme preference"""
    from pathlib import Path
    import json
    
    theme_file = Path("settings/theme.json")
    if theme_file.exists():
        try:
            with open(theme_file, 'r') as f:
                data = json.load(f)
                return data.get("theme", "studio")
        except:
            pass
    return "studio"

def save_theme(theme_name: str):
    """Save theme preference"""
    from pathlib import Path
    import json
    
    theme_file = Path("settings/theme.json")
    theme_file.parent.mkdir(exist_ok=True)
    
    with open(theme_file, 'w') as f:
        json.dump({"theme": theme_name}, f, indent=2)


# Default warning points (percentage-based)
DEFAULT_WARNINGS = [
    {
        "percentage": 50,
        "color": "timer_warning_50",  # References theme color key
        "sound": "assets/Universfield_newnotif10.wav"
    },
    {
        "percentage": 10,
        "color": "timer_warning_10",  # References theme color key
        "sound": "assets/Universfield_newnotif10.wav"
    }
]


def load_warnings() -> list:
    """Load custom warning points from settings"""
    from pathlib import Path
    import json
    
    warnings_file = Path("settings/warnings.json")
    if warnings_file.exists():
        try:
            with open(warnings_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return DEFAULT_WARNINGS.copy()


def save_warnings(warnings: list):
    """Save custom warning points"""
    from pathlib import Path
    import json
    
    warnings_file = Path("settings/warnings.json")
    warnings_file.parent.mkdir(exist_ok=True)
    
    with open(warnings_file, 'w') as f:
        json.dump(warnings, f, indent=2)


def get_text_color_for_bg(bg_color: str) -> str:
    """
    Calculate appropriate text color (black or white) based on background brightness.
    Uses relative luminance formula to determine if background is light or dark.
    
    Args:
        bg_color: Hex color code (e.g., "#4a6fa5" or "#e8e8e8")
    
    Returns:
        "#000000" for light backgrounds, "#ffffff" for dark backgrounds
    """
    # Remove # if present
    hex_color = bg_color.lstrip('#')
    
    # Convert to RGB
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    
    # Calculate relative luminance (perceived brightness)
    # Formula from WCAG: https://www.w3.org/TR/WCAG20/#relativeluminancedef
    def adjust(c):
        if c <= 0.03928:
            return c / 12.92
        else:
            return ((c + 0.055) / 1.055) ** 2.4
    
    r = adjust(r)
    g = adjust(g)
    b = adjust(b)
    
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    # If luminance > 0.5, background is light, use dark text
    # Otherwise, background is dark, use light text
    if luminance > 0.5:
        return "#000000"  # Dark text for light backgrounds
    else:
        return "#ffffff"  # Light text for dark backgrounds


def load_custom_themes() -> dict:
    """Load user-created custom themes"""
    from pathlib import Path
    import json
    
    themes_file = Path("settings/custom_themes.json")
    if themes_file.exists():
        try:
            with open(themes_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_custom_theme(theme_id: str, theme_data: dict):
    """Save a custom theme"""
    from pathlib import Path
    import json
    
    themes_file = Path("settings/custom_themes.json")
    themes_file.parent.mkdir(exist_ok=True)
    
    custom_themes = load_custom_themes()
    custom_themes[theme_id] = theme_data
    
    with open(themes_file, 'w') as f:
        json.dump(custom_themes, f, indent=2)


def delete_custom_theme(theme_id: str):
    """Delete a custom theme"""
    from pathlib import Path
    import json
    
    themes_file = Path("settings/custom_themes.json")
    custom_themes = load_custom_themes()
    
    if theme_id in custom_themes:
        del custom_themes[theme_id]
        
        with open(themes_file, 'w') as f:
            json.dump(custom_themes, f, indent=2)


def get_all_theme_names() -> list:
    """Get list of all available theme names (presets + custom)"""
    preset_names = list(THEMES.keys())
    custom_names = list(load_custom_themes().keys())
    return preset_names + custom_names


def save_canvas_override(canvas_color: str):
    """Save canvas background color override (applies to all themes)"""
    from pathlib import Path
    import json
    
    override_file = Path("settings/canvas_override.json")
    override_file.parent.mkdir(exist_ok=True)
    
    with open(override_file, 'w') as f:
        json.dump({"canvas_bg": canvas_color}, f, indent=2)


def load_canvas_override() -> str:
    """Load canvas background override if it exists"""
    from pathlib import Path
    import json
    
    override_file = Path("settings/canvas_override.json")
    if override_file.exists():
        try:
            with open(override_file, 'r') as f:
                data = json.load(f)
                return data.get("canvas_bg")
        except:
            pass
    return None


def get_canvas_bg(theme: dict) -> str:
    """Get canvas background color, checking override first"""
    override = load_canvas_override()
    if override:
        return override
    return theme.get("canvas_bg", "#808080")