"""
Settings dialog with keyboard shortcuts
"""

import customtkinter as ctk
from typing import Optional
from controllers.keyboard_shortcuts import KeyboardShortcutsManager


class SettingsDialog(ctk.CTkToplevel):
    """Settings dialog with collapsible keyboard shortcuts editor"""
    
    def __init__(self, parent, shortcuts_manager: KeyboardShortcutsManager):
        super().__init__(parent)
        
        self.shortcuts_manager = shortcuts_manager
        self.shortcuts_expanded = False
        
        # Dialog setup
        self.title("Settings")
        self.geometry("550x480")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.center_on_parent(parent)
        
        # Load theme colors
        from theme_config import get_theme, load_current_theme
        theme = get_theme(load_current_theme())
        
        # Colors (match your theme)
        self.CYBER_PINK = theme["primary"]
        self.CYBER_PURPLE = theme["accent"]
        self.CYBER_BLUE = theme["secondary"]
        self.CYBER_GREEN = theme["success"]
        self.CYBER_TEAL = theme["success"]
        self.CYBER_DARK = theme["dark"]
        self.CYBER_GRAY = theme["gray"]
        self.CYBER_LIGHT_GRAY = theme["light_gray"]
        self.CYBER_TEXT = theme["text"]
        # Calculate appropriate text colors based on button backgrounds
        from theme_config import get_text_color_for_bg
        self.CYBER_TEXT_PRIMARY = get_text_color_for_bg(theme["primary"])
        self.CYBER_TEXT_SECONDARY = get_text_color_for_bg(theme["secondary"])
        self.CYBER_TEXT_ACCENT = get_text_color_for_bg(theme["accent"])
        
        self.configure(fg_color=self.CYBER_DARK)
        
        # Track if any shortcuts were edited
        self.shortcuts_changed = False
        self.theme_changed = False
        
        # Build UI
        self.create_widgets()
    
    def center_on_parent(self, parent):
        """Center dialog on parent window"""
        self.update_idletasks()
        
        dialog_width = 550
        dialog_height = 480
        
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Keep on screen
        x = max(20, min(x, screen_width - dialog_width - 20))
        y = max(20, min(y, screen_height - dialog_height - 20))
        
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def create_widgets(self):
        """Build the settings UI"""
        self.main_frame = ctk.CTkFrame(self, fg_color=self.CYBER_DARK)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkLabel(
            self.main_frame,
            text="⚙ Settings",
            font=("Arial", 20, "bold"),
            text_color=self.CYBER_BLUE
        )
        header.pack(pady=(0, 20))
        
        # Create all content
        self.create_content_frame()
        
        # Restart notification area (placeholder)
        self.restart_notice_container = ctk.CTkFrame(self.main_frame, fg_color=self.CYBER_DARK, height=0)
        self.restart_notice_container.pack(fill="x", pady=(0, 15))
        
        # Actual restart notification
        self.restart_notice = ctk.CTkFrame(
            self.restart_notice_container,
            fg_color=self.CYBER_PINK,
            corner_radius=8
        )
        # Don't pack yet
        
        self.restart_notice_label = ctk.CTkLabel(
            self.restart_notice,
            text="⚠️ Restart app for shortcut changes to take effect",
            font=("Arial", 11, "bold"),
            text_color="#000000"
        )
        self.restart_notice_label.pack(padx=15, pady=8)
        
        # Buttons at bottom
        button_frame = ctk.CTkFrame(self.main_frame, fg_color=self.CYBER_DARK)
        button_frame.pack(fill="x")
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            command=self.close_dialog,
            font=("Arial", 13),
            fg_color=self.CYBER_GREEN,
            hover_color=self.CYBER_TEAL,
            text_color="#000000",
            width=120,
            height=35
        )
        close_btn.pack(side="right")
    
    
    def create_volume_section(self):
        """Create volume control sliders"""
        volume_container = ctk.CTkFrame(self.content_frame, fg_color=self.CYBER_LIGHT_GRAY, corner_radius=8)
        volume_container.pack(fill="x", padx=10, pady=10)
        
        # Header
        volume_header = ctk.CTkLabel(
            volume_container,
            text="🔊 Sound Volume",
            font=("Arial", 14, "bold"),
            text_color=self.CYBER_BLUE
        )
        volume_header.pack(pady=(15, 10), padx=15, anchor="w")
        
        # Load current volumes
        from pathlib import Path
        import json
        
        volume_file = Path("settings/volume.json")
        default_volumes = {"warning": 0.7, "transition": 1.0}
        
        if volume_file.exists():
            with open(volume_file, 'r') as f:
                volumes = json.load(f)
        else:
            volumes = default_volumes
        
        # Warning sound volume
        warning_frame = ctk.CTkFrame(volume_container, fg_color="transparent")
        warning_frame.pack(fill="x", padx=15, pady=5)
        
        warning_label = ctk.CTkLabel(
            warning_frame,
            text="⚠️ Warning Sound:",
            font=("Arial", 12),
        )
        warning_label.pack(side="left", padx=(0, 10))
        
        self.warning_volume_value = ctk.CTkLabel(
            warning_frame,
            text=f"{int(volumes['warning'] * 100)}%",
            font=("Arial", 11),
            text_color=self.CYBER_PINK,
            width=40
        )
        self.warning_volume_value.pack(side="right")
        
        self.warning_slider = ctk.CTkSlider(
            volume_container,
            from_=0,
            to=1,
            number_of_steps=20,
            command=lambda v: self.update_volume_label(v, "warning"),
            button_color=self.CYBER_PINK,
            button_hover_color=self.CYBER_PURPLE,
            progress_color=self.CYBER_PINK
        )
        self.warning_slider.set(volumes['warning'])
        self.warning_slider.pack(fill="x", padx=15, pady=(0, 15))
        
        # Transition sound volume
        transition_frame = ctk.CTkFrame(volume_container, fg_color="transparent")
        transition_frame.pack(fill="x", padx=15, pady=5)
        
        transition_label = ctk.CTkLabel(
            transition_frame,
            text="🔔 Transition Sound:",
            font=("Arial", 12),
        )
        transition_label.pack(side="left", padx=(0, 10))
        
        self.transition_volume_value = ctk.CTkLabel(
            transition_frame,
            text=f"{int(volumes['transition'] * 100)}%",
            font=("Arial", 11),
            text_color=self.CYBER_BLUE,
            width=40
        )
        self.transition_volume_value.pack(side="right")
        
        self.transition_slider = ctk.CTkSlider(
            volume_container,
            from_=0,
            to=1,
            number_of_steps=20,
            command=lambda v: self.update_volume_label(v, "transition"),
            button_color=self.CYBER_BLUE,
            button_hover_color=self.CYBER_TEAL,
            progress_color=self.CYBER_BLUE
        )
        self.transition_slider.set(volumes['transition'])
        self.transition_slider.pack(fill="x", padx=15, pady=(0, 15))
        
        # Sound file selection (transition only - warnings set in Warning Points section)
        sound_file_header = ctk.CTkLabel(
            volume_container,
            text="Transition Sound File:",
            font=("Arial", 12, "bold"),
            text_color=self.CYBER_TEXT
        )
        sound_file_header.pack(pady=(5, 5), padx=15, anchor="w")
        
        # Load current sound paths
        sound_file = Path("settings/sounds.json")
        default_sounds = {
            "transition": "assets/Universfield_messageincoming2.wav"
        }
        
        if sound_file.exists():
            with open(sound_file, 'r') as f:
                sound_paths = json.load(f)
        else:
            sound_paths = default_sounds
        
        # Transition sound file
        transition_file_frame = ctk.CTkFrame(volume_container, fg_color="transparent")
        transition_file_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        transition_file_label = ctk.CTkLabel(
            transition_file_frame,
            text="🔔 Transition:",
            font=("Arial", 11),
            text_color=self.CYBER_TEXT,
            width=80
        )
        transition_file_label.pack(side="left")
        
        transition_filename = Path(sound_paths.get('transition', default_sounds['transition'])).name
        self.transition_file_display = ctk.CTkLabel(
            transition_file_frame,
            text=transition_filename,
            font=("Arial", 10),
            text_color=self.CYBER_BLUE,
            anchor="w"
        )
        self.transition_file_display.pack(side="left", padx=10, fill="x", expand=True)
        
        transition_browse_btn = ctk.CTkButton(
            transition_file_frame,
            text="Browse...",
            command=lambda: self.browse_sound_file("transition"),
            width=80,
            height=25,
            font=("Arial", 10),
            fg_color=self.CYBER_PURPLE,
            text_color=self.CYBER_TEXT_ACCENT,
            hover_color=self.CYBER_PINK
        )
        transition_browse_btn.pack(side="right")
        
        # Store sound paths for saving later
        self.sound_paths = sound_paths
    
    def update_volume_label(self, value, sound_type):
        """Update volume percentage label"""
        percentage = int(value * 100)
        if sound_type == "warning":
            self.warning_volume_value.configure(text=f"{percentage}%")
        else:
            self.transition_volume_value.configure(text=f"{percentage}%")
    
    def browse_sound_file(self, sound_type):
        """Browse for custom sound file"""
        from tkinter import filedialog
        from pathlib import Path
        
        file_path = filedialog.askopenfilename(
            title=f"Select {sound_type.capitalize()} Sound",
            filetypes=[
                ("WAV files", "*.wav"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            # Update the display (only transition now)
            filename = Path(file_path).name
            self.transition_file_display.configure(text=filename)
            
            # Store the path
            self.sound_paths[sound_type] = file_path
    
    def create_theme_section(self):
        """Create theme selection radio buttons"""
        from theme_config import load_current_theme, get_all_theme_names, THEMES, load_custom_themes
        
        # Store reference to theme container for easy refresh
        self.theme_container = ctk.CTkFrame(self.content_frame, fg_color=self.CYBER_LIGHT_GRAY, corner_radius=8)
        self.theme_container.pack(fill="x", padx=10, pady=10)
        
        # Header
        theme_header = ctk.CTkLabel(
            self.theme_container,
            text="🎨 Theme",
            font=("Arial", 14, "bold"),
            text_color=self.CYBER_BLUE
        )
        theme_header.pack(pady=(15, 10), padx=15, anchor="w")
        
        # Canvas Background Color Picker (Quick Access)
        canvas_bg_frame = ctk.CTkFrame(self.theme_container, fg_color="transparent")
        canvas_bg_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        canvas_label = ctk.CTkLabel(
            canvas_bg_frame,
            text="🖼️ Canvas Background:",
            font=("Arial", 12),
            text_color=self.CYBER_TEXT
        )
        canvas_label.pack(side="left", padx=(0, 10))
        
        # Get current canvas color
        from theme_config import get_theme
        current_theme = get_theme(load_current_theme())
        current_canvas_color = current_theme.get("canvas_bg", "#808080")
        
        # Color preview button
        self.canvas_color_btn = ctk.CTkButton(
            canvas_bg_frame,
            text="",
            command=self.change_canvas_color,
            fg_color=current_canvas_color,
            hover_color=current_canvas_color,
            width=40,
            height=25
        )
        self.canvas_color_btn.pack(side="left", padx=5)
        
        # Hex code display
        self.canvas_hex_label = ctk.CTkLabel(
            canvas_bg_frame,
            text=current_canvas_color,
            font=("Arial", 11),
            text_color=self.CYBER_TEXT
        )
        self.canvas_hex_label.pack(side="left", padx=5)
        
        # Reset to 50% gray button
        reset_canvas_btn = ctk.CTkButton(
            canvas_bg_frame,
            text="Reset to 50% Gray",
            command=lambda: self.set_canvas_color("#808080"),
            font=("Arial", 10),
            fg_color=self.CYBER_GRAY,
            hover_color=self.CYBER_LIGHT_GRAY,
            text_color=self.CYBER_TEXT,
            width=120,
            height=25
        )
        reset_canvas_btn.pack(side="left", padx=5)
        
        # Separator
        separator = ctk.CTkFrame(self.theme_container, fg_color=self.CYBER_GRAY, height=1)
        separator.pack(fill="x", padx=15, pady=(0, 10))
        
        # Load current theme
        current_theme = load_current_theme()
        self.selected_theme = ctk.StringVar(value=current_theme)
        
        # Theme options frame
        themes_frame = ctk.CTkFrame(self.theme_container, fg_color="transparent")
        themes_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        # Preset themes
        preset_label = ctk.CTkLabel(
            themes_frame,
            text="Preset Themes:",
            font=("Arial", 11, "bold"),
            text_color=self.CYBER_TEXT
        )
        preset_label.pack(anchor="w", pady=(0, 5))
        
        for theme_key, theme_data in THEMES.items():
            radio_btn = ctk.CTkRadioButton(
                themes_frame,
                text=theme_data["name"],
                variable=self.selected_theme,
                value=theme_key,
                font=("Arial", 12),
                fg_color=self.CYBER_PURPLE,
                text_color=self.CYBER_TEXT_ACCENT,
                hover_color=self.CYBER_PINK,
                radiobutton_width=20,
                radiobutton_height=20,
                command=self.on_theme_changed
            )
            radio_btn.pack(anchor="w", pady=3)
        
        # Custom themes
        custom_themes = load_custom_themes()
        if custom_themes:
            custom_label = ctk.CTkLabel(
                themes_frame,
                text="Custom Themes:",
                font=("Arial", 11, "bold"),
                text_color=self.CYBER_TEXT
            )
            custom_label.pack(anchor="w", pady=(10, 5))
            
            for theme_key, theme_data in custom_themes.items():
                theme_frame = ctk.CTkFrame(themes_frame, fg_color="transparent")
                theme_frame.pack(anchor="w", fill="x", pady=2)
                
                radio_btn = ctk.CTkRadioButton(
                    theme_frame,
                    text=theme_data.get("name", theme_key),
                    variable=self.selected_theme,
                    value=theme_key,
                    font=("Arial", 12),
                    fg_color=self.CYBER_PURPLE,
                    text_color=self.CYBER_TEXT_ACCENT,
                    hover_color=self.CYBER_PINK,
                    radiobutton_width=20,
                    radiobutton_height=20,
                    command=self.on_theme_changed
                )
                radio_btn.pack(side="left")
                
                # Delete custom theme button
                delete_btn = ctk.CTkButton(
                    theme_frame,
                    text="✕",
                    command=lambda tk=theme_key: self.delete_custom_theme(tk),
                    font=("Arial", 12, "bold"),
                    fg_color="transparent",
                    hover_color="#ff4444",
                    text_color=self.CYBER_TEXT,
                    width=25,
                    height=20
                )
                delete_btn.pack(side="left", padx=5)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(self.theme_container, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=15, pady=(10, 15))
        
        # Create/Edit custom theme button
        create_theme_btn = ctk.CTkButton(
            buttons_frame,
            text="✏️ Create Custom Theme",
            command=self.open_theme_editor,
            font=("Arial", 12),
            fg_color=self.CYBER_PURPLE,
            text_color=self.CYBER_TEXT_ACCENT,
            hover_color=self.CYBER_PINK,
            height=30
        )
        create_theme_btn.pack(side="left", padx=(0, 5))
        
        # Edit current theme button (if it's custom or to create variant)
        edit_theme_btn = ctk.CTkButton(
            buttons_frame,
            text="📝 Edit Current Theme",
            command=self.edit_current_theme,
            font=("Arial", 12),
            fg_color=self.CYBER_BLUE,
            text_color=self.CYBER_TEXT_SECONDARY,
            hover_color=self.CYBER_PURPLE,
            height=30
        )
        edit_theme_btn.pack(side="left")
    
    def on_theme_changed(self):
        """Called when theme selection changes"""
        self.theme_changed = True
        self.show_restart_notice()
    
    def delete_custom_theme(self, theme_key: str):
        """Delete a custom theme"""
        from theme_config import delete_custom_theme, load_current_theme
        
        # Don't allow deleting if it's the current theme
        current = load_current_theme()
        if theme_key == current:
            # Can't delete active theme - just return
            return
        
        # Delete the theme
        delete_custom_theme(theme_key)
        
        # Rebuild just the theme section
        if hasattr(self, 'theme_container'):
            self.theme_container.destroy()
        self.create_theme_section()
    
    def create_content_frame(self):
        """Recreate content frame with all sections"""
        # Create or recreate scrollable content area
        if hasattr(self, 'content_frame'):
            self.content_frame.destroy()
        
        self.content_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color=self.CYBER_GRAY,
            height=250
        )
        self.content_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Recreate all sections
        self.create_volume_section()
        self.create_theme_section()
        self.create_warnings_section()
        self.create_shortcuts_section()
    
    def open_theme_editor(self):
        """Open theme editor to create new custom theme"""
        ThemeEditorDialog(self, base_theme=None, callback=self.on_theme_saved)
    
    def edit_current_theme(self):
        """Edit current theme (creates a variant if preset)"""
        from theme_config import load_current_theme
        current = load_current_theme()
        ThemeEditorDialog(self, base_theme=current, callback=self.on_theme_saved)
    
    def on_theme_saved(self):
        """Called when a theme is saved from editor"""
        # Destroy and rebuild just the theme section
        if hasattr(self, 'theme_container'):
            self.theme_container.destroy()
        self.create_theme_section()
    
    def change_canvas_color(self):
        """Open color picker for canvas background"""
        import tkinter.colorchooser as colorchooser
        
        current_color = self.canvas_hex_label.cget("text")
        
        color = colorchooser.askcolor(
            color=current_color,
            title="Choose Canvas Background Color",
            parent=self
        )
        
        if color and color[1]:
            self.set_canvas_color(color[1])
    
    def set_canvas_color(self, hex_color: str):
        """Set canvas background color and save to current theme"""
        from theme_config import load_current_theme, save_canvas_override
        
        # Update UI
        self.canvas_color_btn.configure(fg_color=hex_color, hover_color=hex_color)
        self.canvas_hex_label.configure(text=hex_color)
        
        # Save as global override (applies to all themes)
        save_canvas_override(hex_color)
        
        # Update main window canvas immediately if possible
        if hasattr(self.master, 'image_canvas'):
            self.master.image_canvas.configure(bg=hex_color)

    
    def create_warnings_section(self):
        """Create custom warning points section"""
        from theme_config import load_warnings
        
        warnings_container = ctk.CTkFrame(self.content_frame, fg_color=self.CYBER_LIGHT_GRAY, corner_radius=8)
        warnings_container.pack(fill="x", padx=10, pady=10)
        
        # Header
        warnings_header = ctk.CTkLabel(
            warnings_container,
            text="⚠️ Warning Points",
            font=("Arial", 14, "bold"),
        )
        warnings_header.pack(pady=(15, 5), padx=15, anchor="w")
        
        # Description
        desc_label = ctk.CTkLabel(
            warnings_container,
            text="Configure when warnings sound and timer color changes (based on % remaining)",
            font=("Arial", 10),
            text_color=self.CYBER_TEXT
        )
        desc_label.pack(pady=(0, 10), padx=15, anchor="w")
        
        # Load current warnings
        self.warnings = load_warnings()
        
        # Warnings list frame
        self.warnings_list_frame = ctk.CTkFrame(warnings_container, fg_color="transparent")
        self.warnings_list_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        self.build_warnings_list()
        
        # Add warning button
        add_btn = ctk.CTkButton(
            warnings_container,
            text="+ Add Warning",
            command=self.add_warning,
            font=("Arial", 12),
            fg_color=self.CYBER_PURPLE,
            text_color=self.CYBER_TEXT_ACCENT,
            hover_color=self.CYBER_PINK,
            width=120,
            height=30
        )
        add_btn.pack(pady=(0, 15))
    
    def build_warnings_list(self):
        """Build the list of warning entries"""
        # Clear existing
        for widget in self.warnings_list_frame.winfo_children():
            widget.destroy()
        
        # Sort warnings by percentage
        sorted_warnings = sorted(self.warnings, key=lambda w: w['percentage'], reverse=True)
        
        for idx, warning in enumerate(sorted_warnings):
            self.create_warning_entry(idx, warning)
    
    def create_warning_entry(self, idx: int, warning: dict):
        """Create a single warning entry in the list"""
        entry_frame = ctk.CTkFrame(self.warnings_list_frame, fg_color=self.CYBER_GRAY, corner_radius=4)
        entry_frame.pack(fill="x", pady=2)
        
        # Warning label
        warning_label = ctk.CTkLabel(
            entry_frame,
            text=f"Warning at {warning['percentage']}% remaining",
            font=("Arial", 11, "bold"),
            text_color=self.CYBER_TEXT
        )
        warning_label.pack(side="left", padx=10, pady=8)
        
        # Get actual color from theme
        from theme_config import get_theme, load_current_theme
        theme = get_theme(load_current_theme())
        warning_color = warning.get('color_hex') or theme.get(warning.get('color', 'timer_warning_10'), '#ff6b35')
        
        # Color display button
        color_btn = ctk.CTkButton(
            entry_frame,
            text="",
            command=lambda: self.pick_color(idx),
            fg_color=warning_color,
            hover_color=warning_color,
            width=30,
            height=25,
            corner_radius=4
        )
        color_btn.pack(side="right", padx=5)
        
        # Sound file label and button
        sound_filename = warning.get('sound', 'bell.wav').split('/')[-1]
        sound_btn = ctk.CTkButton(
            entry_frame,
            text=f"🔔 {sound_filename[:15]}",
            command=lambda: self.pick_sound(idx),
            font=("Arial", 10),
            fg_color="transparent",
            hover_color=self.CYBER_PURPLE,
            text_color=self.CYBER_TEXT,
            width=120,
            height=25
        )
        sound_btn.pack(side="right", padx=5)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            entry_frame,
            text="✕",
            command=lambda: self.delete_warning(idx),
            font=("Arial", 14, "bold"),
            fg_color="transparent",
            hover_color="#ff4444",
            text_color=self.CYBER_TEXT,
            width=30,
            height=25
        )
        delete_btn.pack(side="right", padx=5)
    
    def add_warning(self):
        """Add a new warning point"""
        # Simple dialog to get percentage
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Warning")
        dialog.geometry("300x150")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center on parent
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 300) // 2
        y = self.winfo_y() + (self.winfo_height() - 150) // 2
        dialog.geometry(f"300x150+{x}+{y}")
        
        dialog.configure(fg_color=self.CYBER_DARK)
        
        # Label
        label = ctk.CTkLabel(
            dialog,
            text="Warning at % remaining:",
            font=("Arial", 12),
            text_color=self.CYBER_TEXT
        )
        label.pack(pady=(20, 5))
        
        # Entry
        entry = ctk.CTkEntry(
            dialog,
            font=("Arial", 12),
            width=100
        )
        entry.pack(pady=5)
        entry.insert(0, "25")
        entry.focus()
        
        def save_warning():
            try:
                percentage = int(entry.get())
                if 1 <= percentage <= 99:
                    # Add warning with default color based on percentage
                    if percentage >= 50:
                        color_key = "timer_warning_50"
                    else:
                        color_key = "timer_warning_10"
                    
                    new_warning = {
                        "percentage": percentage,
                        "color": color_key,
                        "sound": "assets/bell.wav"
                    }
                    self.warnings.append(new_warning)
                    self.build_warnings_list()
                    dialog.destroy()
            except ValueError:
                pass
        
        # Save button
        save_btn = ctk.CTkButton(
            dialog,
            text="Add",
            command=save_warning,
            font=("Arial", 12),
            fg_color=self.CYBER_GREEN,
            hover_color=self.CYBER_TEAL,
            text_color="#000000",
            width=100
        )
        save_btn.pack(pady=10)
        
        entry.bind("<Return>", lambda e: save_warning())
    
    def delete_warning(self, idx: int):
        """Delete a warning point"""
        sorted_warnings = sorted(self.warnings, key=lambda w: w['percentage'], reverse=True)
        warning_to_remove = sorted_warnings[idx]
        self.warnings.remove(warning_to_remove)
        self.build_warnings_list()
    
    def pick_color(self, idx: int):
        """Open color picker for a warning"""
        import tkinter.colorchooser as colorchooser
        
        sorted_warnings = sorted(self.warnings, key=lambda w: w['percentage'], reverse=True)
        warning = sorted_warnings[idx]
        
        # Get current color
        from theme_config import get_theme, load_current_theme
        theme = get_theme(load_current_theme())
        current_color = warning.get('color_hex') or theme.get(warning.get('color', 'timer_warning_10'), '#ff6b35')
        
        # Open color picker
        color = colorchooser.askcolor(
            color=current_color,
            title=f"Choose color for {warning['percentage']}% warning",
            parent=self
        )
        
        if color and color[1]:  # color[1] is the hex string
            # Find the warning in the original list and update it
            for w in self.warnings:
                if w['percentage'] == warning['percentage']:
                    w['color_hex'] = color[1]
                    break
            self.build_warnings_list()
    
    def pick_sound(self, idx: int):
        """Open file picker for warning sound"""
        from tkinter import filedialog
        
        sorted_warnings = sorted(self.warnings, key=lambda w: w['percentage'], reverse=True)
        warning = sorted_warnings[idx]
        
        # Open file picker
        filename = filedialog.askopenfilename(
            title=f"Select sound for {warning['percentage']}% warning",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
            parent=self
        )
        
        if filename:
            # Find the warning in the original list and update it
            for w in self.warnings:
                if w['percentage'] == warning['percentage']:
                    w['sound'] = filename
                    break
            self.build_warnings_list()


    
    def create_shortcuts_section(self):
        """Create collapsible keyboard shortcuts section"""
        # Section header
        header_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=self.CYBER_LIGHT_GRAY,
            corner_radius=8
        )
        header_frame.pack(fill="x", pady=(0, 5))
        
        # Make entire header clickable
        header_button = ctk.CTkButton(
            header_frame,
            text="⌨️ Keyboard Shortcuts  ▼",
            command=self.toggle_shortcuts,
            font=("Arial", 14, "bold"),
            fg_color="transparent",
            hover_color=self.CYBER_GRAY,
            text_color=self.CYBER_PURPLE,
            anchor="w",
            height=40
        )
        header_button.pack(fill="x", padx=10, pady=5)
        
        self.shortcuts_toggle_button = header_button
        
        # Container for shortcuts
        self.shortcuts_container = ctk.CTkFrame(
            self.content_frame,
            fg_color=self.CYBER_DARK
        )
        # Don't pack yet
    
    def toggle_shortcuts(self):
        """Expand or collapse keyboard shortcuts"""
        self.shortcuts_expanded = not self.shortcuts_expanded
        
        if self.shortcuts_expanded:
            # Show shortcuts
            self.shortcuts_toggle_button.configure(text="⌨️ Keyboard Shortcuts  ▲")
            self.shortcuts_container.pack(fill="x", pady=(0, 10))
            self.build_shortcuts_ui()
        else:
            # Hide shortcuts
            self.shortcuts_toggle_button.configure(text="⌨️ Keyboard Shortcuts  ▼")
            self.shortcuts_container.pack_forget()
    
    def build_shortcuts_ui(self):
        """Build the keyboard shortcuts editor UI"""
        # Clear existing widgets
        for widget in self.shortcuts_container.winfo_children():
            widget.destroy()
        
        # Info text
        info_label = ctk.CTkLabel(
            self.shortcuts_container,
            text="Click on a key to change it. Secondary keys are optional.",
            font=("Arial", 10),
            text_color=self.CYBER_TEXT
        )
        info_label.pack(pady=(10, 15))
        
        # Get all shortcuts
        shortcuts = self.shortcuts_manager.get_all_shortcuts()
        
        # Create row for each action
        for action, binding in shortcuts.items():
            self.create_shortcut_row(action, binding)
        
        # Reset button
        reset_frame = ctk.CTkFrame(self.shortcuts_container, fg_color=self.CYBER_DARK)
        reset_frame.pack(fill="x", pady=(15, 10))
        
        reset_btn = ctk.CTkButton(
            reset_frame,
            text="↻ Reset to Defaults",
            command=self.reset_shortcuts,
            font=("Arial", 11),
            fg_color=self.CYBER_GRAY,
            hover_color=self.CYBER_LIGHT_GRAY,
            text_color=self.CYBER_TEXT,
            width=140,
            height=30
        )
        reset_btn.pack()
    
    def create_shortcut_row(self, action: str, binding):
        """Create a row for one shortcut"""
        row_frame = ctk.CTkFrame(
            self.shortcuts_container,
            fg_color=self.CYBER_GRAY,
            corner_radius=6
        )
        row_frame.pack(fill="x", padx=10, pady=3)
        
        # Action name
        action_label = ctk.CTkLabel(
            row_frame,
            text=self.shortcuts_manager.get_action_display_name(action),
            font=("Arial", 12),
            text_color=self.CYBER_TEXT,
            anchor="w",
            width=150
        )
        action_label.pack(side="left", padx=15, pady=10)
        
        # Keys container
        keys_frame = ctk.CTkFrame(row_frame, fg_color=self.CYBER_GRAY)
        keys_frame.pack(side="right", padx=10, pady=5)
        
        # Primary key button
        primary_display = self.shortcuts_manager.get_key_display_name(binding.primary)
        primary_btn = ctk.CTkButton(
            keys_frame,
            text=primary_display,
            command=lambda: self.edit_key(action, "primary"),
            font=("Arial", 11, "bold"),
            fg_color=self.CYBER_BLUE,
            text_color=self.CYBER_TEXT_SECONDARY,
            hover_color=self.CYBER_PURPLE,
            width=80,
            height=30
        )
        primary_btn.pack(side="left", padx=3)
        
        # Secondary key button
        secondary_display = self.shortcuts_manager.get_key_display_name(binding.secondary) if binding.secondary else "---"
        secondary_btn = ctk.CTkButton(
            keys_frame,
            text=secondary_display,
            command=lambda: self.edit_key(action, "secondary"),
            font=("Arial", 11, "bold"),
            fg_color=self.CYBER_LIGHT_GRAY if binding.secondary else self.CYBER_GRAY,
            hover_color=self.CYBER_PURPLE,
            text_color=self.CYBER_TEXT,
            width=80,
            height=30
        )
        secondary_btn.pack(side="left", padx=3)
    
    def edit_key(self, action: str, key_type: str):
        """Open dialog to edit a key binding"""
        KeyEditDialog(self, self.shortcuts_manager, action, key_type, self.on_key_edited)
    
    def on_key_edited(self):
        """Called when a key is edited"""
        self.shortcuts_changed = True
        self.show_restart_notice()
        self.build_shortcuts_ui()  # Refresh the UI
    
    def reset_shortcuts(self):
        """Reset all shortcuts to defaults"""
        self.shortcuts_manager.reset_to_defaults()
        self.shortcuts_changed = True
        self.show_restart_notice()
        self.build_shortcuts_ui()
    
    def show_restart_notice(self):
        """Show the restart notification"""
        if not self.restart_notice.winfo_ismapped():
            self.restart_notice.pack(fill="x", padx=5, pady=5)
            # Force update to make it visible immediately
            self.update_idletasks()
    
    def close_dialog(self):
        """Close the dialog and save volume settings"""
        # Save volume settings
        from pathlib import Path
        import json
        from theme_config import save_theme, save_warnings
        
        volumes = {
            "warning": self.warning_slider.get(),
            "transition": self.transition_slider.get()
        }
        
        volume_file = Path("settings/volume.json")
        volume_file.parent.mkdir(exist_ok=True)
        
        with open(volume_file, 'w') as f:
            json.dump(volumes, f, indent=2)
        
        # Save sound file paths
        sound_file = Path("settings/sounds.json")
        with open(sound_file, 'w') as f:
            json.dump(self.sound_paths, f, indent=2)
        
        # Save theme
        if hasattr(self, 'selected_theme'):
            save_theme(self.selected_theme.get())
        
        # Save warning points
        if hasattr(self, 'warnings'):
            save_warnings(self.warnings)
        
        self.grab_release()
        self.destroy()

class ThemeEditorDialog(ctk.CTkToplevel):
    """Dialog for creating/editing custom themes"""
    
    def __init__(self, parent, base_theme=None, callback=None):
        super().__init__(parent)
        
        self.callback = callback
        self.base_theme = base_theme
        
        # Load theme to edit
        from theme_config import get_theme, THEMES
        if base_theme:
            self.theme_data = get_theme(base_theme).copy()
            self.title(f"Edit Theme - {self.theme_data.get('name', base_theme)}")
            # If editing a preset, suggest a variant name
            if base_theme in THEMES:
                self.theme_data['name'] = f"{self.theme_data['name']} (Custom)"
        else:
            # Start from Studio theme as default
            self.theme_data = get_theme("studio").copy()
            self.theme_data['name'] = "My Custom Theme"
            self.title("Create Custom Theme")
        
        self.geometry("500x700")
        self.resizable(False, True)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 500) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 700) // 2
        self.geometry(f"500x700+{x}+{y}")
        
        # Colors for UI (use parent's colors)
        self.CYBER_DARK = parent.CYBER_DARK
        self.CYBER_GRAY = parent.CYBER_GRAY
        self.CYBER_LIGHT_GRAY = parent.CYBER_LIGHT_GRAY
        self.CYBER_TEXT = parent.CYBER_TEXT
        self.CYBER_BLUE = parent.CYBER_BLUE
        self.CYBER_PURPLE = parent.CYBER_PURPLE
        self.CYBER_PINK = parent.CYBER_PINK
        self.CYBER_GREEN = parent.CYBER_GREEN
        
        self.configure(fg_color=self.CYBER_DARK)
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create theme editor UI"""
        main_frame = ctk.CTkFrame(self, fg_color=self.CYBER_DARK)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkLabel(
            main_frame,
            text="🎨 Theme Editor",
            font=("Arial", 18, "bold"),
            text_color=self.CYBER_BLUE
        )
        header.pack(pady=(0, 15))
        
        # Theme name
        name_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        name_frame.pack(fill="x", pady=(0, 15))
        
        name_label = ctk.CTkLabel(
            name_frame,
            text="Theme Name:",
            font=("Arial", 12),
            text_color=self.CYBER_TEXT
        )
        name_label.pack(side="left", padx=(0, 10))
        
        self.name_entry = ctk.CTkEntry(
            name_frame,
            font=("Arial", 12),
            width=250
        )
        self.name_entry.insert(0, self.theme_data.get('name', 'My Custom Theme'))
        self.name_entry.pack(side="left")
        
        # Scrollable color pickers
        scroll_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color=self.CYBER_GRAY,
            height=450
        )
        scroll_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Store color entries
        self.color_entries = {}
        
        # Color categories
        categories = [
            ("Backgrounds", ["dark", "gray", "light_gray"]),  # Removed canvas_bg - use Settings instead
            ("Accent Colors", ["primary", "secondary", "accent", "success"]),
            ("UI Colors", ["text", "warning"]),
            ("Timer Colors", ["timer", "timer_normal", "timer_warning_50", "timer_warning_10"])
        ]
        
        for category_name, color_keys in categories:
            # Category header
            cat_label = ctk.CTkLabel(
                scroll_frame,
                text=category_name,
                font=("Arial", 13, "bold"),
                text_color=self.CYBER_BLUE
            )
            cat_label.pack(anchor="w", pady=(10, 5), padx=10)
            
            for key in color_keys:
                if key in self.theme_data:
                    self.create_color_picker(scroll_frame, key, self.theme_data[key])
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            font=("Arial", 12),
            fg_color=self.CYBER_GRAY,
            hover_color=self.CYBER_LIGHT_GRAY,
            width=100
        )
        cancel_btn.pack(side="left", padx=5)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Theme",
            command=self.save_theme,
            font=("Arial", 12, "bold"),
            fg_color=self.CYBER_GREEN,
            hover_color=self.CYBER_PURPLE,
            text_color="#000000",
            width=150
        )
        save_btn.pack(side="right", padx=5)
    
    def create_color_picker(self, parent, key: str, color: str):
        """Create a color picker row"""
        row_frame = ctk.CTkFrame(parent, fg_color="transparent")
        row_frame.pack(fill="x", padx=10, pady=3)
        
        # Label
        label_text = key.replace("_", " ").title()
        label = ctk.CTkLabel(
            row_frame,
            text=label_text + ":",
            font=("Arial", 11),
            text_color=self.CYBER_TEXT,
            width=150,
            anchor="w"
        )
        label.pack(side="left")
        
        # Color display button
        color_btn = ctk.CTkButton(
            row_frame,
            text="",
            command=lambda: self.pick_color(key),
            fg_color=color,
            hover_color=color,
            width=40,
            height=25
        )
        color_btn.pack(side="left", padx=5)
        
        # Color hex entry
        entry = ctk.CTkEntry(
            row_frame,
            font=("Arial", 11),
            width=100
        )
        entry.insert(0, color)
        entry.pack(side="left", padx=5)
        
        self.color_entries[key] = (entry, color_btn)
    
    def pick_color(self, key: str):
        """Open color picker for a theme color"""
        import tkinter.colorchooser as colorchooser
        
        entry, color_btn = self.color_entries[key]
        current_color = entry.get()
        
        color = colorchooser.askcolor(
            color=current_color,
            title=f"Choose {key.replace('_', ' ').title()}",
            parent=self
        )
        
        if color and color[1]:
            entry.delete(0, 'end')
            entry.insert(0, color[1])
            color_btn.configure(fg_color=color[1], hover_color=color[1])
    
    def save_theme(self):
        """Save the custom theme"""
        from theme_config import save_custom_theme
        import re
        
        # Get theme name
        theme_name = self.name_entry.get().strip()
        if not theme_name:
            return
        
        # Create theme ID (lowercase, no spaces)
        theme_id = re.sub(r'[^a-z0-9]+', '_', theme_name.lower())
        
        # Gather all colors
        new_theme = {
            "name": theme_name
        }
        
        for key, (entry, _) in self.color_entries.items():
            new_theme[key] = entry.get()
        
        # Save
        save_custom_theme(theme_id, new_theme)
        
        # Callback to refresh parent
        if self.callback:
            self.callback()
        
        self.destroy()


class KeyEditDialog(ctk.CTkToplevel):
    """Small dialog to capture a new key binding"""
    
    def __init__(self, parent, shortcuts_manager, action: str, key_type: str, callback):
        super().__init__(parent)
        
        self.shortcuts_manager = shortcuts_manager
        self.action = action
        self.key_type = key_type  # "primary" or "secondary"
        self.callback = callback
        
        # Dialog setup
        self.title("Press a Key")
        self.geometry("350x200")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center
        self.center_on_parent(parent)
        
        # Colors
        self.CYBER_BLUE = "#67E8F9"
        self.CYBER_PINK = "#FF6EC7"
        self.CYBER_DARK = "#0f0f0f"
        self.CYBER_GRAY = "#1f1f1f"
        self.CYBER_TEXT = "#E5E5E5"
        
        self.configure(fg_color=self.CYBER_DARK)
        
        # Build UI
        self.create_widgets()
        
        # Bind key press
        self.bind("<Key>", self.on_key_press)
        
        if self.key_type == "secondary":
            self.bind("<Escape>", lambda e: self.clear_key())
        else:
            self.bind("<Escape>", lambda e: self.cancel())
    
    def center_on_parent(self, parent):
        """Center on parent"""
        self.update_idletasks()
        
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        x = parent_x + (parent_width - 350) // 2
        y = parent_y + (parent_height - 200) // 2
        
        self.geometry(f"350x200+{x}+{y}")
    
    def create_widgets(self):
        """Build UI"""
        main_frame = ctk.CTkFrame(self, fg_color=self.CYBER_DARK)
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Action name
        action_name = self.shortcuts_manager.get_action_display_name(self.action)
        label = ctk.CTkLabel(
            main_frame,
            text=f"Set {self.key_type} key for:",
            font=("Arial", 12),
        )
        label.pack(pady=(0, 5))
        
        action_label = ctk.CTkLabel(
            main_frame,
            text=action_name,
            font=("Arial", 16, "bold"),
            text_color=self.CYBER_BLUE
        )
        action_label.pack(pady=(0, 20))
        
        # Instruction
        if self.key_type == "secondary":
            instruction_text = "Press any key...\n(ESC to clear)"
        else:
            instruction_text = "Press any key...\n(ESC to cancel)"
        
        instruction = ctk.CTkLabel(
            main_frame,
            text=instruction_text,
            font=("Arial", 13),
            text_color=self.CYBER_TEXT
        )
        instruction.pack(pady=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color=self.CYBER_DARK)
        button_frame.pack(pady=(20, 0))
        
        # Clear button
        if self.key_type == "secondary":
            clear_btn = ctk.CTkButton(
                button_frame,
                text="Clear",
                command=self.clear_key,
                font=("Arial", 11),
                fg_color=self.CYBER_GRAY,
                hover_color=self.CYBER_PINK,
                width=80,
                height=30
            )
            clear_btn.pack(side="left", padx=5)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel,
            font=("Arial", 11),
            fg_color=self.CYBER_GRAY,
            hover_color=self.CYBER_PINK,
            width=80,
            height=30
        )
        cancel_btn.pack(side="left", padx=5)
    
    def on_key_press(self, event):
        """Handle key press"""
        key = event.keysym
        
        # Ignore modifier keys alone
        if key in ["Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R"]:
            return
        
        # Get current binding
        binding = self.shortcuts_manager.get_shortcut(self.action)
        
        # Update the binding
        if self.key_type == "primary":
            self.shortcuts_manager.update_shortcut(
                self.action,
                primary=key,
                secondary=binding.secondary
            )
        else:  # secondary
            self.shortcuts_manager.update_shortcut(
                self.action,
                primary=binding.primary,
                secondary=key
            )
        
        # Notify parent and close
        self.callback()
        self.grab_release()
        self.destroy()
    
    def clear_key(self):
        """Clear secondary key"""
        binding = self.shortcuts_manager.get_shortcut(self.action)
        self.shortcuts_manager.update_shortcut(
            self.action,
            primary=binding.primary,
            secondary=None
        )
        self.callback()
        self.grab_release()
        self.destroy()
    
    def cancel(self):
        """Cancel without changes"""
        self.grab_release()
        self.destroy()