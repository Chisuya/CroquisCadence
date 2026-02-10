import customtkinter as ctk
from typing import Optional, List
from models.session import Session, SessionBlock
import json
from pathlib import Path


class SessionBuilderDialog(ctk.CTkToplevel):
    """Dialog for building custom drawing sessions"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Dialog setup
        self.title("Create Custom Session")
        self.geometry("600x800")
        self.resizable(False, False)
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        
        # Position mid-right
        self.update_idletasks()
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        dialog_width = 600
        dialog_height = 800
        
        # Position: right side with margin, vertically centered
        x = screen_width - dialog_width - 50
        y = (screen_height - dialog_height) // 2
        
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # State
        self.blocks: List[SessionBlock] = []
        self.result: Optional[Session] = None
        
        # Colors
        self.CYBER_PINK = "#FF6EC7"
        self.CYBER_PURPLE = "#B794F6"
        self.CYBER_BLUE = "#67E8F9"
        self.CYBER_GREEN = "#67F971"
        self.CYBER_TEAL = "#1CBC7C"
        self.CYBER_DARK = "#0f0f0f"
        self.CYBER_GRAY = "#1f1f1f"
        self.CYBER_LIGHT_GRAY = "#2a2a2a"
        self.CYBER_TEXT = "#E5E5E5"
        
        self.configure(fg_color=self.CYBER_DARK)
        
        # Presets management
        self.presets_file = Path("user_data/session_presets.json")
        self.presets_file.parent.mkdir(parents=True, exist_ok=True)
        self.custom_presets = self.load_presets()
        
        # Build UI
        self.create_widgets()
    
    def create_widgets(self):
        """Create all dialog widgets"""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color=self.CYBER_DARK)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Session name section
        name_frame = ctk.CTkFrame(main_frame, fg_color=self.CYBER_GRAY)
        name_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            name_frame,
            text="Session Name:",
            font=("Arial", 14, "bold"),
            text_color=self.CYBER_BLUE
        ).pack(side="left", padx=10, pady=10)
        
        self.name_entry = ctk.CTkEntry(
            name_frame,
            placeholder_text="My Custom Session",
            font=("Arial", 14),
            width=350
        )
        self.name_entry.pack(side="left", padx=10, pady=10)
        
        # Preset templates section
        preset_container = ctk.CTkFrame(main_frame, fg_color=self.CYBER_LIGHT_GRAY)
        preset_container.pack(fill="x", pady=(0, 15))
        
        # Header row
        preset_header = ctk.CTkFrame(preset_container, fg_color=self.CYBER_LIGHT_GRAY)
        preset_header.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            preset_header,
            text="Quick Start Presets:",
            font=("Arial", 13, "bold"),
            text_color=self.CYBER_PURPLE
        ).pack(side="left")
        
        manage_btn = ctk.CTkButton(
            preset_header,
            text="⚙ Manage",
            command=self.open_manage_presets,
            font=("Arial", 11),
            fg_color=self.CYBER_GRAY,
            hover_color=self.CYBER_LIGHT_GRAY,
            width=80,
            height=25
        )
        manage_btn.pack(side="right")
        
        # Container for preset buttons with fixed height
        preset_scroll_container = ctk.CTkFrame(
            preset_container,
            fg_color=self.CYBER_LIGHT_GRAY,
            height=80
        )
        preset_scroll_container.pack(fill="x", padx=10, pady=(0, 10))
        preset_scroll_container.pack_propagate(False)  # Keep fixed height
        
        # Scrollable preset buttons area
        self.preset_buttons_frame = ctk.CTkScrollableFrame(
            preset_scroll_container,
            fg_color=self.CYBER_LIGHT_GRAY
        )
        self.preset_buttons_frame.pack(fill="both", expand=True)
        
        self.refresh_preset_buttons()
        
        # Blocks list section
        blocks_label = ctk.CTkLabel(
            main_frame,
            text="Blocks:",
            font=("Arial", 16, "bold"),
            text_color=self.CYBER_PURPLE,
            anchor="w"
        )
        blocks_label.pack(fill="x", pady=(0, 10))
        
        # Scrollable frame for blocks
        self.blocks_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color=self.CYBER_LIGHT_GRAY,
            height=200
        )
        self.blocks_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Total duration display
        self.duration_label = ctk.CTkLabel(
            main_frame,
            text="Total Duration: 0m 0s",
            font=("Arial", 14, "bold"),
            text_color=self.CYBER_GREEN
        )
        self.duration_label.pack(fill="x", pady=(0, 15))
        
        # Add block section
        add_frame = ctk.CTkFrame(main_frame, fg_color=self.CYBER_GRAY)
        add_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            add_frame,
            text="Add Block:",
            font=("Arial", 14, "bold"),
            text_color=self.CYBER_PINK
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        # Type selection
        type_frame = ctk.CTkFrame(add_frame, fg_color=self.CYBER_GRAY)
        type_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            type_frame,
            text="Type:",
            font=("Arial", 12),
            text_color=self.CYBER_TEXT
        ).pack(side="left", padx=(0, 10))
        
        self.block_type = ctk.StringVar(value="pose")
        
        ctk.CTkRadioButton(
            type_frame,
            text="Pose",
            variable=self.block_type,
            value="pose",
            font=("Arial", 12),
            fg_color=self.CYBER_BLUE,
            hover_color=self.CYBER_PURPLE
        ).pack(side="left", padx=5)
        
        ctk.CTkRadioButton(
            type_frame,
            text="Break",
            variable=self.block_type,
            value="break",
            font=("Arial", 12),
            fg_color=self.CYBER_PINK,
            hover_color=self.CYBER_PURPLE
        ).pack(side="left", padx=5)
        
        # Count and duration inputs
        input_frame = ctk.CTkFrame(add_frame, fg_color=self.CYBER_GRAY)
        input_frame.pack(fill="x", padx=15, pady=5)
        
        # Count
        ctk.CTkLabel(
            input_frame,
            text="Count:",
            font=("Arial", 12),
            text_color=self.CYBER_TEXT
        ).pack(side="left", padx=(0, 5))
        
        self.count_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="10",
            font=("Arial", 12),
            width=60
        )
        self.count_entry.pack(side="left", padx=5)
        self.count_entry.insert(0, "1")
        
        # Duration value
        ctk.CTkLabel(
            input_frame,
            text="Duration:",
            font=("Arial", 12),
            text_color=self.CYBER_TEXT
        ).pack(side="left", padx=(15, 5))
        
        self.duration_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="30",
            font=("Arial", 12),
            width=60
        )
        self.duration_entry.pack(side="left", padx=5)
        self.duration_entry.insert(0, "30")
        
        # Duration unit
        self.duration_unit = ctk.StringVar(value="seconds")
        
        unit_menu = ctk.CTkOptionMenu(
            input_frame,
            values=["seconds", "minutes", "hours"],
            variable=self.duration_unit,
            font=("Arial", 12),
            width=100,
            fg_color=self.CYBER_PURPLE,
            button_color=self.CYBER_PURPLE,
            button_hover_color=self.CYBER_BLUE
        )
        unit_menu.pack(side="left", padx=5)
        
        # Add button
        add_btn = ctk.CTkButton(
            add_frame,
            text="+ Add Block",
            command=self.add_block,
            font=("Arial", 13, "bold"),
            fg_color=self.CYBER_GREEN,
            hover_color=self.CYBER_TEAL,
            text_color="#000000",
            height=35
        )
        add_btn.pack(fill="x", padx=15, pady=(10, 15))
        
        # Bottom buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color=self.CYBER_DARK)
        button_frame.pack(fill="x")
        
        save_preset_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save as Preset",
            command=self.save_as_preset,
            font=("Arial", 12),
            fg_color=self.CYBER_BLUE,
            hover_color=self.CYBER_PURPLE,
            text_color="#000000",
            width=140,
            height=40
        )
        save_preset_btn.pack(side="left", padx=(0, 10))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel,
            font=("Arial", 13),
            fg_color=self.CYBER_GRAY,
            hover_color=self.CYBER_LIGHT_GRAY,
            text_color="#FFFFFF",
            width=100,
            height=40
        )
        cancel_btn.pack(side="left", padx=(0, 10))
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Start",
            command=self.save_and_start,
            font=("Arial", 13, "bold"),
            fg_color=self.CYBER_PINK,
            hover_color=self.CYBER_PURPLE,
            text_color="#FFFFFF",
            width=150,
            height=40
        )
        save_btn.pack(side="right")
    
    def add_block(self):
        """Add a new block to the session"""
        try:
            # Get values
            block_type = self.block_type.get()
            count = int(self.count_entry.get())
            duration_value = int(self.duration_entry.get())
            duration_unit = self.duration_unit.get()
            
            # Convert duration to seconds
            if duration_unit == "minutes":
                duration_seconds = duration_value * 60
            elif duration_unit == "hours":
                duration_seconds = duration_value * 3600
            else:
                duration_seconds = duration_value
            
            # Validation
            if count <= 0 or duration_seconds <= 0:
                self.show_error("Count and duration must be positive!")
                return
            
            # Create block
            block = SessionBlock(
                block_type=block_type,
                duration=duration_seconds,
                count=count,
                folder_paths=None
            )
            
            # Add to list
            self.blocks.append(block)
            
            # Update UI
            self.refresh_blocks_list()
            self.update_total_duration()
            
        except ValueError:
            self.show_error("Please enter valid numbers!")
    
    def refresh_blocks_list(self):
        """Refresh the blocks display"""
        # Clear existing widgets
        for widget in self.blocks_frame.winfo_children():
            widget.destroy()
        
        # Add each block
        for idx, block in enumerate(self.blocks):
            self.create_block_widget(idx, block)
    
    def create_block_widget(self, idx: int, block: SessionBlock):
        """Create a widget for a single block"""
        frame = ctk.CTkFrame(self.blocks_frame, fg_color=self.CYBER_GRAY)
        frame.pack(fill="x", pady=5, padx=5)
        
        # Block info
        if block.block_type == "pose":
            if block.duration < 60:
                duration_str = f"{block.duration}s"
            elif block.duration < 3600:
                minutes = block.duration // 60
                duration_str = f"{minutes}m"
            else:
                hours = block.duration // 3600
                minutes = (block.duration % 3600) // 60
                if minutes > 0:
                    duration_str = f"{hours}h {minutes}m"
                else:
                    duration_str = f"{hours}h"
            
            text = f"{idx + 1}. {block.count} poses × {duration_str}"
            color = self.CYBER_BLUE
        else:
            minutes = block.duration // 60
            text = f"{idx + 1}. Break × {minutes}m"
            color = self.CYBER_PINK
        
        label = ctk.CTkLabel(
            frame,
            text=text,
            font=("Arial", 13),
            text_color=color,
            anchor="w",
            width=350
        )
        label.pack(side="left", padx=10, pady=8)
        
        # Control buttons
        btn_frame = ctk.CTkFrame(frame, fg_color=self.CYBER_GRAY)
        btn_frame.pack(side="right", padx=5)
        
        # Move up
        if idx > 0:
            up_btn = ctk.CTkButton(
                btn_frame,
                text="↑",
                command=lambda: self.move_block_up(idx),
                width=30,
                height=30,
                fg_color=self.CYBER_PURPLE,
                hover_color=self.CYBER_BLUE,
                font=("Arial", 16)
            )
            up_btn.pack(side="left", padx=2)
        
        # Move down
        if idx < len(self.blocks) - 1:
            down_btn = ctk.CTkButton(
                btn_frame,
                text="↓",
                command=lambda: self.move_block_down(idx),
                width=30,
                height=30,
                fg_color=self.CYBER_PURPLE,
                hover_color=self.CYBER_BLUE,
                font=("Arial", 16)
            )
            down_btn.pack(side="left", padx=2)
        
        # Delete
        del_btn = ctk.CTkButton(
            btn_frame,
            text="×",
            command=lambda: self.delete_block(idx),
            width=30,
            height=30,
            fg_color=self.CYBER_PINK,
            hover_color="#FF4444",
            font=("Arial", 18, "bold")
        )
        del_btn.pack(side="left", padx=2)
    
    def move_block_up(self, idx: int):
        """Move block up in the list"""
        if idx > 0:
            self.blocks[idx], self.blocks[idx - 1] = self.blocks[idx - 1], self.blocks[idx]
            self.refresh_blocks_list()
    
    def move_block_down(self, idx: int):
        """Move block down in the list"""
        if idx < len(self.blocks) - 1:
            self.blocks[idx], self.blocks[idx + 1] = self.blocks[idx + 1], self.blocks[idx]
            self.refresh_blocks_list()
    
    def delete_block(self, idx: int):
        """Delete a block"""
        self.blocks.pop(idx)
        self.refresh_blocks_list()
        self.update_total_duration()
    
    def update_total_duration(self):
        """Update the total duration display"""
        if not self.blocks:
            self.duration_label.configure(text="Total Duration: 0m 0s")
            return
        
        total_seconds = sum(block.total_duration() for block in self.blocks)
        
        hours, remaining = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remaining, 60)
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0:
            parts.append(f"{seconds}s")
        
        duration_str = " ".join(parts) if parts else "0s"
        self.duration_label.configure(text=f"Total Duration: {duration_str}")
    
    def show_error(self, message: str):
        """Show an error message"""
        # error display
        error_label = ctk.CTkLabel(
            self.blocks_frame,
            text=f"⚠️ {message}",
            font=("Arial", 12),
            text_color="#FF4444"
        )
        error_label.pack(pady=10)
        
        # rm after 3 seconds
        self.after(3000, error_label.destroy)
    
    def cancel(self):
        """Cancel and close dialog"""
        self.result = None
        self.grab_release()
        self.destroy()
    
    def save_and_start(self):
        """Save session and close dialog"""
        if not self.blocks:
            self.show_error("Please add at least one block!")
            return
        
        # Get session name
        name = self.name_entry.get().strip()
        if not name:
            name = "Custom Session"
        
        # Expand blocks with count > 1 into individual blocks
        expanded_blocks = []
        for block in self.blocks:
            for _ in range(block.count):
                expanded_blocks.append(
                    SessionBlock(
                        block_type=block.block_type,
                        duration=block.duration,
                        count=1,
                        folder_paths=block.folder_paths
                    )
                )
        self.result = Session(name=name, blocks=expanded_blocks)
        
        self.grab_release()
        self.destroy()
    
    def get_result(self) -> Optional[Session]:
        """Get the created session (call after dialog closes)"""
        return self.result
    
    def load_1hr_class_preset(self):
        """Load the 1 Hr Class Mode preset"""

        self.blocks = []
        
        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, "1 Hr Class Mode")
        
        # Add blocks
        # 10 poses, 30 seconds each
        self.blocks.append(SessionBlock(block_type="pose", duration=30, count=10, folder_paths=None))
        
        # 5 poses, 1 minute each
        self.blocks.append(SessionBlock(block_type="pose", duration=60, count=5, folder_paths=None))
        
        # 2 poses, 5 minutes each
        self.blocks.append(SessionBlock(block_type="pose", duration=300, count=2, folder_paths=None))
        
        # 1 pose, 10 minutes
        self.blocks.append(SessionBlock(block_type="pose", duration=600, count=1, folder_paths=None))
        
        # Break, 5 minutes
        self.blocks.append(SessionBlock(block_type="break", duration=300, count=1))
        
        # 1 pose, 25 minutes
        self.blocks.append(SessionBlock(block_type="pose", duration=1500, count=1, folder_paths=None))
        
        # Refresh display
        self.refresh_blocks_list()
        self.update_total_duration()
    
    def load_warmup_preset(self):
        """Load a quick warmup preset"""
        # Clear existing blocks
        self.blocks = []
        
        # Set session name
        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, "Quick Warmup")
        
        # Add blocks
        # 20 poses, 15 seconds each (5 minutes total)
        self.blocks.append(SessionBlock(block_type="pose", duration=15, count=20, folder_paths=None))
        
        # 10 poses, 30 seconds each (5 minutes total)
        self.blocks.append(SessionBlock(block_type="pose", duration=30, count=10, folder_paths=None))
        
        # Refresh display
        self.refresh_blocks_list()
        self.update_total_duration()
    
    def load_presets(self) -> dict:
        """Load saved presets from file"""
        if not self.presets_file.exists():
            return {}
        
        try:
            with open(self.presets_file, 'r') as f:
                data = json.load(f)
                return data
        except Exception as e:
            print(f"Error loading presets: {e}")
            return {}
    
    def save_presets(self):
        """Save presets to file"""
        try:
            with open(self.presets_file, 'w') as f:
                json.dump(self.custom_presets, f, indent=2)
        except Exception as e:
            print(f"Error saving presets: {e}")
    
    def refresh_preset_buttons(self):
        """Refresh the preset buttons display"""
        # Clear existing buttons
        for widget in self.preset_buttons_frame.winfo_children():
            widget.destroy()
        
        # Built in presets (always show)
        builtin_frame = ctk.CTkFrame(self.preset_buttons_frame, fg_color=self.CYBER_LIGHT_GRAY)
        builtin_frame.pack(fill="x", pady=2)
        
        ctk.CTkButton(
            builtin_frame,
            text="📚 1 Hr Class Mode",
            command=self.load_1hr_class_preset,
            font=("Arial", 11),
            fg_color=self.CYBER_PURPLE,
            hover_color=self.CYBER_BLUE,
            text_color="#FFFFFF",
            width=140,
            height=28
        ).pack(side="left", padx=2, pady=2)
        
        ctk.CTkButton(
            builtin_frame,
            text="🔥 Quick Warmup",
            command=self.load_warmup_preset,
            font=("Arial", 11),
            fg_color=self.CYBER_PINK,
            hover_color=self.CYBER_PURPLE,
            text_color="#FFFFFF",
            width=140,
            height=28
        ).pack(side="left", padx=2, pady=2)
        
        # Custom presets
        if self.custom_presets:
            for preset_name in self.custom_presets.keys():
                custom_frame = ctk.CTkFrame(self.preset_buttons_frame, fg_color=self.CYBER_LIGHT_GRAY)
                custom_frame.pack(fill="x", pady=2)
                
                ctk.CTkButton(
                    custom_frame,
                    text=f"⭐ {preset_name}",
                    command=lambda name=preset_name: self.load_custom_preset(name),
                    font=("Arial", 11),
                    fg_color=self.CYBER_GREEN,
                    hover_color=self.CYBER_TEAL,
                    text_color="#000000",
                    width=280,
                    height=28,
                    anchor="w"
                ).pack(side="left", padx=2, pady=2)
    
    def load_custom_preset(self, preset_name: str):
        """Load a custom preset by name"""
        if preset_name not in self.custom_presets:
            return
        
        preset_data = self.custom_presets[preset_name]
        
        self.blocks = []
        
        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, preset_name)
        
        # Load blocks from preset
        for block_data in preset_data['blocks']:
            self.blocks.append(
                SessionBlock(
                    block_type=block_data['block_type'],
                    duration=block_data['duration'],
                    count=block_data['count'],
                    folder_paths=block_data.get('folder_paths')
                )
            )
        
        self.refresh_blocks_list()
        self.update_total_duration()
    
    def save_as_preset(self):
        """Save current session configuration as a preset"""
        if not self.blocks:
            self.show_error("Please add at least one block before saving!")
            return
        
        # Create input dialog
        dialog = ctk.CTkInputDialog(
            text="Enter preset name:",
            title="Save Preset"
        )
        preset_name = dialog.get_input()
        
        if not preset_name:
            return  # User cancelled
        
        preset_data = {
            'blocks': [
                {
                    'block_type': block.block_type,
                    'duration': block.duration,
                    'count': block.count,
                    'folder_paths': block.folder_paths
                }
                for block in self.blocks
            ]
        }
        
        self.custom_presets[preset_name] = preset_data
        self.save_presets()
        
        self.refresh_preset_buttons()
        
        confirm_label = ctk.CTkLabel(
            self.preset_buttons_frame,
            text=f"✅ Saved '{preset_name}'!",
            font=("Arial", 11, "bold"),
            text_color=self.CYBER_GREEN
        )
        confirm_label.pack(pady=5)
        self.after(2000, confirm_label.destroy)
    
    def open_manage_presets(self):
        """Open preset management dialog"""
        ManagePresetsDialog(self, self.custom_presets, self.on_presets_updated)
    
    def on_presets_updated(self, updated_presets: dict):
        """Called when presets are modified in manage dialog"""
        self.custom_presets = updated_presets
        self.save_presets()
        self.refresh_preset_buttons()


class ManagePresetsDialog(ctk.CTkToplevel):
    """Dialog for managing saved presets"""
    
    def __init__(self, parent, presets: dict, on_update_callback):
        super().__init__(parent)
        
        self.presets = presets.copy()
        self.on_update_callback = on_update_callback
        
        # Dialog setup
        self.title("Manage Presets")
        self.geometry("500x400")
        self.resizable(False, False)
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        
        # Mid-right screen pos
        self.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        dialog_width = 500
        dialog_height = 400
        
        # Position: right side with margin, vertically centered
        x = screen_width - dialog_width - 50
        y = (screen_height - dialog_height) // 2
        
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Colors
        self.CYBER_PINK = "#FF6EC7"
        self.CYBER_BLUE = "#67E8F9"
        self.CYBER_GREEN = "#67F971"
        self.CYBER_DARK = "#0f0f0f"
        self.CYBER_GRAY = "#1f1f1f"
        self.CYBER_LIGHT_GRAY = "#2a2a2a"
        self.CYBER_TEXT = "#E5E5E5"
        
        self.configure(fg_color=self.CYBER_DARK)
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ctk.CTkFrame(self, fg_color=self.CYBER_DARK)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        header = ctk.CTkLabel(
            main_frame,
            text="Manage Your Presets",
            font=("Arial", 18, "bold"),
            text_color=self.CYBER_BLUE
        )
        header.pack(pady=(0, 20))
        
        # Info text
        info = ctk.CTkLabel(
            main_frame,
            text="Built-in presets (1 Hr Class Mode, Quick Warmup) cannot be deleted.",
            font=("Arial", 11),
            text_color=self.CYBER_TEXT,
            wraplength=450
        )
        info.pack(pady=(0, 15))
        
        # Scrollable preset list
        self.preset_list_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color=self.CYBER_LIGHT_GRAY,
            height=200
        )
        self.preset_list_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        self.refresh_preset_list()
        
        # Close button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Close",
            command=self.close_dialog,
            font=("Arial", 13),
            fg_color=self.CYBER_GRAY,
            hover_color=self.CYBER_LIGHT_GRAY,
            width=120,
            height=40
        )
        close_btn.pack()
    
    def refresh_preset_list(self):
        """Refresh the preset list display"""
        for widget in self.preset_list_frame.winfo_children():
            widget.destroy()
        
        if not self.presets:
            no_presets_label = ctk.CTkLabel(
                self.preset_list_frame,
                text="No custom presets saved yet.\nCreate one in the Session Builder!",
                font=("Arial", 12),
                text_color=self.CYBER_TEXT
            )
            no_presets_label.pack(pady=40)
            return
        
        for preset_name, preset_data in self.presets.items():
            self.create_preset_row(preset_name, preset_data)
    
    def create_preset_row(self, preset_name: str, preset_data: dict):
        """Create a row for one preset"""
        row = ctk.CTkFrame(self.preset_list_frame, fg_color=self.CYBER_GRAY)
        row.pack(fill="x", pady=5, padx=5)
        
        # Preset name and info
        info_frame = ctk.CTkFrame(row, fg_color=self.CYBER_GRAY)
        info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=8)
        
        name_label = ctk.CTkLabel(
            info_frame,
            text=f"⭐ {preset_name}",
            font=("Arial", 13, "bold"),
            text_color=self.CYBER_GREEN,
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        # Calculate total blocks
        total_blocks = sum(block['count'] for block in preset_data['blocks'])
        total_seconds = sum(block['duration'] * block['count'] for block in preset_data['blocks'])
        
        hours, remaining = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remaining, 60)
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 and hours == 0:
            parts.append(f"{seconds}s")
        
        duration_str = " ".join(parts) if parts else "0s"
        
        details_label = ctk.CTkLabel(
            info_frame,
            text=f"{total_blocks} blocks • {duration_str}",
            font=("Arial", 11),
            text_color=self.CYBER_TEXT,
            anchor="w"
        )
        details_label.pack(anchor="w")
        
        # Delete button
        delete_btn = ctk.CTkButton(
            row,
            text="🗑 Delete",
            command=lambda: self.delete_preset(preset_name),
            font=("Arial", 11),
            fg_color=self.CYBER_PINK,
            hover_color="#FF4444",
            width=90,
            height=35
        )
        delete_btn.pack(side="right", padx=10)
    
    def delete_preset(self, preset_name: str):
        """Delete a preset"""
        # Confirm deletion
        confirm_dialog = ctk.CTkInputDialog(
            text=f"Delete '{preset_name}'?\nType 'yes' to confirm:",
            title="Confirm Deletion"
        )
        response = confirm_dialog.get_input()
        
        if response and response.lower() == 'yes':
            del self.presets[preset_name]
            self.refresh_preset_list()
    
    def close_dialog(self):
        """Close dialog and update parent"""
        self.on_update_callback(self.presets)
        self.grab_release()
        self.destroy()