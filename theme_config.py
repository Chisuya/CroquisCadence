"""
Theme configuration
"""

THEMES = {
    "cyberpunk": {
        "name": "Cyberpunk",
        "dark": "#0f0f0f",
        "gray": "#1f1f1f",
        "light_gray": "#2a2a2a",
        "primary": "#FF6EC7",
        "secondary": "#67E8F9",
        "accent": "#8B5CF6",
        "success": "#67F971",
        "text": "#E5E5E5",
        "warning": "#FF6EC7",
        "timer": "#FF6EC7",
    },
    "matcha": {
        "name": "Matcha Latte",
        "dark": "#1a1d1a",
        "gray": "#252b25",
        "light_gray": "#303630",
        "primary": "#88b04b",
        "secondary": "#a8d08d",
        "accent": "#6b8e23",
        "success": "#9db07e",
        "text": "#e8f5e9",
        "warning": "#ff6b35",
        "timer": "#d4a574",
    }
}

def get_theme(theme_name: str = "matcha") -> dict:
    """Get theme colors by name"""
    return THEMES.get(theme_name, THEMES["matcha"])

def load_current_theme() -> str:
    """Load saved theme preference"""
    from pathlib import Path
    import json
    
    theme_file = Path("settings/theme.json")
    if theme_file.exists():
        try:
            with open(theme_file, 'r') as f:
                data = json.load(f)
                return data.get("theme", "matcha")
        except:
            pass
    return "matcha"

def save_theme(theme_name: str):
    """Save theme preference"""
    from pathlib import Path
    import json
    
    theme_file = Path("settings/theme.json")
    theme_file.parent.mkdir(exist_ok=True)
    
    with open(theme_file, 'w') as f:
        json.dump({"theme": theme_name}, f, indent=2)