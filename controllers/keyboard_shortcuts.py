"""
Keyboard shortcuts manager for CroquisCadence
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict


@dataclass
class KeyBinding:
    """Keyboard shortcut with primary and optional secondary key"""
    action: str
    primary: str
    secondary: Optional[str] = None
    
    def get_all_keys(self) -> List[str]:
        """Get list of all keys (primary + secondary if set)"""
        keys = [self.primary]
        if self.secondary:
            keys.append(self.secondary)
        return keys


class KeyboardShortcutsManager:
    """Manages keyboard shortcuts and persistence"""
    
    # Default keybindings
    DEFAULT_SHORTCUTS = {
        "pause_resume": KeyBinding(
            action="pause_resume",
            primary="Return",  # Enter key
            secondary="space"
        ),
        "previous_image": KeyBinding(
            action="previous_image",
            primary="Left",
            secondary="a"
        ),
        "next_image": KeyBinding(
            action="next_image",
            primary="Right",
            secondary="d"
        ),
        "previous_block": KeyBinding(
            action="previous_block",
            primary="Up",
            secondary="w"
        ),
        "next_block": KeyBinding(
            action="next_block",
            primary="Down",
            secondary="s"
        ),
    }
    
    def __init__(self, settings_file: Path = Path("user_data/settings.json")):
        """
        Initialize shortcuts manager
        
        Args:
            settings_file: Path to settings.json
        """
        self.settings_file = settings_file
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.shortcuts: Dict[str, KeyBinding] = {}
        self.callbacks: Dict[str, Callable] = {}
        
        self.load_shortcuts()
    
    def load_shortcuts(self):
        """Load shortcuts from settings file, or use defaults"""
        if not self.settings_file.exists():
            self.shortcuts = self.DEFAULT_SHORTCUTS.copy()
            self.save_shortcuts()
            return
        
        try:
            with open(self.settings_file, 'r') as f:
                data = json.load(f)
            
            # Load keyboard_shortcuts section if it exists
            if "keyboard_shortcuts" in data:
                shortcuts_data = data["keyboard_shortcuts"]
                self.shortcuts = {
                    action: KeyBinding(**binding_data)
                    for action, binding_data in shortcuts_data.items()
                }
            else:
                # No shortcuts in file, use defaults
                self.shortcuts = self.DEFAULT_SHORTCUTS.copy()
                self.save_shortcuts()
        
        except Exception as e:
            print(f"Error loading shortcuts: {e}")
            self.shortcuts = self.DEFAULT_SHORTCUTS.copy()
            self.save_shortcuts()
    
    def save_shortcuts(self):
        """Save shortcuts to settings file"""
        try:
            # Load existing settings
            existing_data = {}
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    existing_data = json.load(f)
            
            # Update keyboard_shortcuts section
            existing_data["keyboard_shortcuts"] = {
                action: asdict(binding)
                for action, binding in self.shortcuts.items()
            }
            
            # Save back to file
            with open(self.settings_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
        
        except Exception as e:
            print(f"Error saving shortcuts: {e}")
    
    def update_shortcut(self, action: str, primary: str, secondary: Optional[str] = None):
        """
        Update a keyboard shortcut
        
        Args:
            action: Action name (e.g., "pause_resume")
            primary: Primary key
            secondary: Optional secondary key
        """
        if action not in self.shortcuts:
            raise ValueError(f"Unknown action: {action}")
        
        self.shortcuts[action] = KeyBinding(
            action=action,
            primary=primary,
            secondary=secondary
        )
        self.save_shortcuts()
    
    def get_shortcut(self, action: str) -> Optional[KeyBinding]:
        """Get keybinding for an action"""
        return self.shortcuts.get(action)
    
    def get_all_shortcuts(self) -> Dict[str, KeyBinding]:
        """Get all keybindings"""
        return self.shortcuts.copy()
    
    def register_callback(self, action: str, callback: Callable):
        """
        Register a callback function for an action
        
        Args:
            action: Action name
            callback: Function to call when shortcut is pressed
        """
        self.callbacks[action] = callback
    
    def handle_key_press(self, key: str) -> bool:
        """
        Handle a key press event
        
        Args:
            key: The key that was pressed (tkinter format)
        
        Returns:
            True if key was handled, False otherwise
        """
        # Normalize key format
        key = self._normalize_key(key)
        
        # Find matching action
        for action, binding in self.shortcuts.items():
            if key in binding.get_all_keys():
                # Call the callback if registered
                if action in self.callbacks:
                    self.callbacks[action]()
                    return True
        
        return False
    
    def _normalize_key(self, key: str) -> str:
        """
        Normalize key format from tkinter to our format
        
        Args:
            key: Key from tkinter event
        
        Returns:
            Normalized key string
        """
        # Convert tkinter key names to our format
        key_mapping = {
            "space": "space",
            "Return": "Return",
            "Left": "Left",
            "Right": "Right",
            "Up": "Up",
            "Down": "Down",
            "a": "a",
            "d": "d",
            "w": "w",
            "s": "s",
        }
        
        return key_mapping.get(key, key)
    
    def reset_to_defaults(self):
        """Reset all shortcuts to defaults"""
        self.shortcuts = self.DEFAULT_SHORTCUTS.copy()
        self.save_shortcuts()
    
    def get_action_display_name(self, action: str) -> str:
        """Get human-readable name for action"""
        display_names = {
            "pause_resume": "Pause/Resume",
            "previous_image": "Previous Image",
            "next_image": "Next Image",
            "previous_block": "Previous Block",
            "next_block": "Next Block",
        }
        return display_names.get(action, action)
    
    def get_key_display_name(self, key: str) -> str:
        """Get human-readable name for key"""
        if not key:
            return ""
        
        display_names = {
            "space": "Space",
            "Return": "Enter",
            "Left": "←",
            "Right": "→",
            "Up": "↑",
            "Down": "↓",
            "a": "A",
            "d": "D",
            "w": "W",
            "s": "S",
        }
        return display_names.get(key, key.capitalize())