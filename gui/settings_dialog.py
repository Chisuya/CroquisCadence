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
        
        # Colors (match your cyberpunk theme)
        self.CYBER_PINK = "#FF6EC7"
        self.CYBER_PURPLE = "#8B5CF6"
        self.CYBER_BLUE = "#67E8F9"
        self.CYBER_GREEN = "#67F971"
        self.CYBER_TEAL = "#1CBC7C"
        self.CYBER_DARK = "#0f0f0f"
        self.CYBER_GRAY = "#1f1f1f"
        self.CYBER_LIGHT_GRAY = "#2a2a2a"
        self.CYBER_TEXT = "#E5E5E5"
        
        self.configure(fg_color=self.CYBER_DARK)
        
        # Track if any shortcuts were edited
        self.shortcuts_changed = False
        
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
        main_frame = ctk.CTkFrame(self, fg_color=self.CYBER_DARK)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkLabel(
            main_frame,
            text="⚙ Settings",
            font=("Arial", 20, "bold"),
            text_color=self.CYBER_BLUE
        )
        header.pack(pady=(0, 20))
        
        # Scrollable content area
        self.content_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color=self.CYBER_GRAY,
            height=250
        )
        self.content_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Volume settings section
        self.create_volume_section()
        
        # Keyboard shortcuts section
        self.create_shortcuts_section()
        
        # Restart notification area (placeholder)
        self.restart_notice_container = ctk.CTkFrame(main_frame, fg_color=self.CYBER_DARK, height=0)
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
        button_frame = ctk.CTkFrame(main_frame, fg_color=self.CYBER_DARK)
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
        default_volumes = {"warning": 0.7, "transition": 0.5}
        
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
            text_color=self.CYBER_TEXT
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
            text_color=self.CYBER_TEXT
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
    
    def update_volume_label(self, value, sound_type):
        """Update volume percentage label"""
        percentage = int(value * 100)
        if sound_type == "warning":
            self.warning_volume_value.configure(text=f"{percentage}%")
        else:
            self.transition_volume_value.configure(text=f"{percentage}%")
    
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
            hover_color=self.CYBER_PURPLE,
            text_color="#000000",
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
        
        volumes = {
            "warning": self.warning_slider.get(),
            "transition": self.transition_slider.get()
        }
        
        volume_file = Path("settings/volume.json")
        volume_file.parent.mkdir(exist_ok=True)
        
        with open(volume_file, 'w') as f:
            json.dump(volumes, f, indent=2)
        
        self.grab_release()
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
            text_color=self.CYBER_TEXT
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