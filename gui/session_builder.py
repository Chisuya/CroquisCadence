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
        self.geometry("1000x720")  # Increased height to 720
        self.resizable(False, False)
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        
        # Position mid-right
        self.update_idletasks()
        
        dialog_width = 1000
        dialog_height = 720

        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = parent_x + parent_width + 20
        y = parent_y + (parent_height - dialog_height) // 2

        if y + dialog_height > screen_height:
            y = screen_height - dialog_height - 20
        
        if y < 20:
            y = 20
        
        if x + dialog_width > screen_width:
            x = parent_x - dialog_width - 20
            if x < 0:
                x = max(20, (screen_width - dialog_width) // 2)
        
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # State
        self.blocks: List[SessionBlock] = []
        self.result: Optional[Session] = None
        self.parent_window = parent
        
        # Colors
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
        
        # Presets management
        self.presets_file = Path("user_data/session_presets.json")
        self.presets_file.parent.mkdir(parents=True, exist_ok=True)
        self.custom_presets = self.load_presets()
        
        # Build UI
        self.create_widgets()
    
    def create_widgets(self):
        """Create all dialog widgets with horizontal layout"""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color=self.CYBER_DARK)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # TOP ROW
        top_section = ctk.CTkFrame(main_frame, fg_color=self.CYBER_DARK)
        top_section.pack(fill="x", pady=(0, 10))
        
        # Session name (left side)
        name_frame = ctk.CTkFrame(top_section, fg_color=self.CYBER_GRAY)
        name_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(
            name_frame,
            text="Session Name:",
            font=("Arial", 13, "bold"),
            text_color=self.CYBER_BLUE
        ).pack(side="left", padx=10, pady=8)
        
        self.name_entry = ctk.CTkEntry(
            name_frame,
            placeholder_text="Enter session name (used for presets)",
            font=("Arial", 13),
            width=250
        )
        self.name_entry.pack(side="left", padx=10, pady=8)
        
        # Total duration (right side)
        self.duration_label = ctk.CTkLabel(
            top_section,
            text="Total: 0m 0s",
            font=("Arial", 13, "bold"),
            text_color=self.CYBER_GREEN,
            fg_color=self.CYBER_GRAY,
            width=150,
            height=40,
            corner_radius=6
        )
        self.duration_label.pack(side="right", padx=0)
        
        # MAIN CONTENT
        content_frame = ctk.CTkFrame(main_frame, fg_color=self.CYBER_DARK)
        content_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Left column
        left_column = ctk.CTkFrame(content_frame, fg_color=self.CYBER_DARK)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Quick start preset
        preset_header = ctk.CTkFrame(left_column, fg_color=self.CYBER_DARK)
        preset_header.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(
            preset_header,
            text="Quick Start:",
            font=("Arial", 12, "bold"),
            text_color=self.CYBER_PURPLE
        ).pack(side="left")
        
        manage_btn = ctk.CTkButton(
            preset_header,
            text="⚙",
            command=self.open_manage_presets,
            font=("Arial", 11),
            fg_color=self.CYBER_GRAY,
            hover_color=self.CYBER_LIGHT_GRAY,
            width=30,
            height=25
        )
        manage_btn.pack(side="right")
        
        # Preset buttons
        preset_buttons_container = ctk.CTkFrame(left_column, fg_color=self.CYBER_LIGHT_GRAY)
        preset_buttons_container.pack(fill="x", pady=(0, 10))
        
        self.preset_buttons_frame = ctk.CTkScrollableFrame(
            preset_buttons_container,
            fg_color=self.CYBER_LIGHT_GRAY,
            height=70,
            orientation="horizontal"
        )
        self.preset_buttons_frame.pack(fill="x", padx=5, pady=5)
        
        self.refresh_preset_buttons()
        
        # Blocks list
        blocks_header = ctk.CTkLabel(
            left_column,
            text="Session Blocks:",
            font=("Arial", 14, "bold"),
            text_color=self.CYBER_PURPLE,
            anchor="w"
        )
        blocks_header.pack(fill="x", pady=(0, 5))
        
        self.blocks_frame = ctk.CTkScrollableFrame(
            left_column,
            fg_color=self.CYBER_LIGHT_GRAY
        )
        self.blocks_frame.pack(fill="both", expand=True)
        
        # Right column
        right_column = ctk.CTkFrame(content_frame, fg_color=self.CYBER_GRAY, corner_radius=10)
        right_column.pack(side="right", fill="both", expand=True)
        
        ctk.CTkLabel(
            right_column,
            text="Add Block:",
            font=("Arial", 14, "bold"),
            text_color=self.CYBER_PINK
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Controls area
        controls_area = ctk.CTkFrame(right_column, fg_color=self.CYBER_GRAY)
        controls_area.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Type selection
        type_frame = ctk.CTkFrame(controls_area, fg_color=self.CYBER_GRAY)
        type_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            type_frame,
            text="Type:",
            font=("Arial", 12, "bold"),
            text_color=self.CYBER_TEXT,
            width=80,
            anchor="w"
        ).pack(side="left")
        
        self.block_type = ctk.StringVar(value="pose")
        
        radio_container = ctk.CTkFrame(type_frame, fg_color=self.CYBER_GRAY)
        radio_container.pack(side="left", fill="x", expand=True)
        
        ctk.CTkRadioButton(
            radio_container,
            text="Pose",
            variable=self.block_type,
            value="pose",
            font=("Arial", 12),
            fg_color=self.CYBER_BLUE,
            hover_color=self.CYBER_PURPLE,
            command=self.on_block_type_changed
        ).pack(side="left", padx=(0, 15))
        
        ctk.CTkRadioButton(
            radio_container,
            text="Break",
            variable=self.block_type,
            value="break",
            font=("Arial", 12),
            fg_color=self.CYBER_PINK,
            hover_color=self.CYBER_PURPLE,
            command=self.on_block_type_changed
        ).pack(side="left")
        
        # Count & Duration
        counts_frame = ctk.CTkFrame(controls_area, fg_color=self.CYBER_GRAY)
        counts_frame.pack(fill="x", pady=(0, 10))
        
        # Count
        count_col = ctk.CTkFrame(counts_frame, fg_color=self.CYBER_GRAY)
        count_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(
            count_col,
            text="Count:",
            font=("Arial", 12, "bold"),
            text_color=self.CYBER_TEXT
        ).pack(anchor="w", pady=(0, 5))
        
        self.count_entry = ctk.CTkEntry(
            count_col,
            placeholder_text="10",
            font=("Arial", 12),
            width=100
        )
        self.count_entry.pack(anchor="w")
        self.count_entry.insert(0, "1")
        
        # Duration
        duration_col = ctk.CTkFrame(counts_frame, fg_color=self.CYBER_GRAY)
        duration_col.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            duration_col,
            text="Duration:",
            font=("Arial", 12, "bold"),
            text_color=self.CYBER_TEXT
        ).pack(anchor="w", pady=(0, 5))
        
        duration_inputs = ctk.CTkFrame(duration_col, fg_color=self.CYBER_GRAY)
        duration_inputs.pack(fill="x")
        
        self.duration_entry = ctk.CTkEntry(
            duration_inputs,
            placeholder_text="30",
            font=("Arial", 12),
            width=70
        )
        self.duration_entry.pack(side="left", padx=(0, 5))
        self.duration_entry.insert(0, "30")
        
        self.duration_unit = ctk.StringVar(value="seconds")
        
        unit_menu = ctk.CTkOptionMenu(
            duration_inputs,
            values=["seconds", "minutes", "hours"],
            variable=self.duration_unit,
            font=("Arial", 11),
            width=100,
            fg_color=self.CYBER_PURPLE,
            button_color=self.CYBER_PURPLE,
            button_hover_color=self.CYBER_BLUE
        )
        unit_menu.pack(side="left")
        
        # Folders section
        folders_frame = ctk.CTkFrame(controls_area, fg_color=self.CYBER_DARK, corner_radius=8)
        folders_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Header with Clear All button
        folders_header = ctk.CTkFrame(folders_frame, fg_color=self.CYBER_DARK)
        folders_header.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            folders_header,
            text="Folders:",
            font=("Arial", 12, "bold"),
            text_color=self.CYBER_BLUE
        ).pack(side="left")
        
        self.clear_all_btn = ctk.CTkButton(
            folders_header,
            text="Clear All",
            command=self.clear_all_folders,
            font=("Arial", 10),
            fg_color=self.CYBER_PINK,
            hover_color="#FF4444",
            text_color="#FFFFFF",
            width=70,
            height=22
        )
        # Don't pack yet
        
        # Selected tags
        self.selected_tags_frame = ctk.CTkFrame(
            folders_frame,
            fg_color=self.CYBER_LIGHT_GRAY,
            height=30
        )
        self.selected_tags_frame.pack(fill="x", padx=10, pady=(0, 5))
        self.selected_tags_frame.pack_propagate(False)
        
        self.selected_folders_set = set()
        self.all_folders_selected = True
        self._create_selected_tag("All Folders", is_all=True)
        
        # Search bar
        search_frame = ctk.CTkFrame(folders_frame, fg_color=self.CYBER_DARK)
        search_frame.pack(fill="x", padx=10, pady=(5, 2))
        
        ctk.CTkLabel(
            search_frame,
            text="🔍",
            font=("Arial", 12),
            text_color=self.CYBER_TEXT
        ).pack(side="left", padx=(0, 5))
        
        self.folder_search_var = ctk.StringVar()
        self.folder_search_var.trace_add("write", self._on_search_changed)
        
        self.folder_search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search folders...",
            font=("Arial", 11),
            textvariable=self.folder_search_var,
            height=28
        )
        self.folder_search_entry.pack(side="left", fill="x", expand=True)
        
        # Available folders, scrollable
        available_scroll = ctk.CTkScrollableFrame(
            folders_frame,
            fg_color=self.CYBER_GRAY,
            height=140
        )
        available_scroll.pack(fill="x", padx=10, pady=(5, 10))
        
        self.available_container = ctk.CTkFrame(available_scroll, fg_color=self.CYBER_GRAY)
        self.available_container.pack(fill="x", expand=True)
        
        self.available_folders = self.get_available_folders()
        self.folder_buttons = {}  # Store buttons for filtering
        
        # Create grid of folder buttons
        self._create_folder_buttons()
        
        # Add Block button
        add_btn = ctk.CTkButton(
            right_column,
            text="+ Add Block",
            command=self.add_block,
            font=("Arial", 13, "bold"),
            fg_color=self.CYBER_GREEN,
            hover_color=self.CYBER_TEAL,
            text_color="#000000",
            height=40
        )
        add_btn.pack(fill="x", padx=15, pady=(0, 15))
        
        # Bottom row
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
            
            # Get folder selection
            folder_paths = None
            if block_type == "pose":
                if self.all_folders_selected:
                    folder_paths = None
                else:
                    folder_paths = sorted(list(self.selected_folders_set)) if self.selected_folders_set else None
            
            # Create block
            block = SessionBlock(
                block_type=block_type,
                duration=duration_seconds,
                count=count,
                folder_paths=folder_paths
            )
            
            # Add to list
            self.blocks.append(block)
            
            # Update UI
            self.refresh_blocks_list()
            self.update_total_duration()
            
        except ValueError:
            self.show_error("Please enter valid numbers!")

    def get_available_folders(self):
        """Get list of available image folders from parent's image collection"""
        try:
            if hasattr(self.parent_window, 'image_collection'):
                folders = self.parent_window.image_collection.get_folder_list()
                return folders if folders else []
        except Exception as e:
            print(f"Error getting folders: {e}")
        return []

    def on_block_type_changed(self):
        pass

    def _create_selected_tag(self, folder_name: str, is_all: bool = False):
        """Create a selected tag pill with X button"""
        tag_frame = ctk.CTkFrame(
            self.selected_tags_frame,
            fg_color=self.CYBER_PINK if is_all else self.CYBER_PURPLE,
            corner_radius=12,
            height=25
        )
        tag_frame.pack(side="left", padx=3, pady=2)
        
        ctk.CTkLabel(
            tag_frame,
            text=folder_name,
            font=("Arial", 10, "bold" if is_all else "normal"),
            text_color="#FFFFFF"
        ).pack(side="left", padx=(8, 4), pady=2)
        
        if not is_all or len(self.selected_folders_set) > 0:
            x_btn = ctk.CTkButton(
                tag_frame,
                text="×",
                font=("Arial", 14, "bold"),
                fg_color="transparent",
                hover_color=self.CYBER_DARK,
                text_color="#FFFFFF",
                width=20,
                height=20,
                command=lambda: self.remove_folder_tag(folder_name, is_all)
            )
            x_btn.pack(side="left", padx=(0, 4), pady=2)

    def _create_folder_buttons(self, filter_text: str = ""):
        """Create or recreate folder buttons with optional filtering"""
        # Clear existing buttons
        for widget in self.available_container.winfo_children():
            widget.destroy()
        self.folder_buttons.clear()
        
        # Filter folders based on search text
        filtered_folders = [
            f for f in self.available_folders 
            if filter_text.lower() in f.lower()
        ]
        
        # Sort alphabetically
        filtered_folders.sort(key=str.lower)
        
        if not filtered_folders:
            # Show no results message
            no_results = ctk.CTkLabel(
                self.available_container,
                text="No folders match search",
                font=("Arial", 11),
                text_color=self.CYBER_TEXT
            )
            no_results.grid(row=0, column=0, columnspan=2, pady=20)
            return
        
        # Create grid of folder buttons
        tags_per_row = 2
        for idx, folder in enumerate(filtered_folders):
            row = idx // tags_per_row
            col = idx % tags_per_row
            
            tag_btn = ctk.CTkButton(
                self.available_container,
                text=folder,
                font=("Arial", 10),
                fg_color=self.CYBER_PURPLE,
                hover_color=self.CYBER_BLUE,
                text_color="#FFFFFF",
                height=24,
                corner_radius=12,
                command=lambda f=folder: self.add_folder_tag(f)
            )
            tag_btn.grid(row=row, column=col, padx=3, pady=3, sticky="ew")
            self.folder_buttons[folder] = tag_btn
        
        # Configure grid columns
        self.available_container.grid_columnconfigure(0, weight=1)
        self.available_container.grid_columnconfigure(1, weight=1)
    
    def _on_search_changed(self, *args):
        """Called when search text changes"""
        search_text = self.folder_search_var.get()
        self._create_folder_buttons(search_text)
    
    def clear_all_folders(self):
        """Clear all selected folders and return to 'All Folders'"""
        self.selected_folders_set.clear()
        self.all_folders_selected = True
        self._refresh_selected_tags()
    
    def _update_clear_button_visibility(self):
        """Show/hide Clear All button based on selection state"""
        if self.all_folders_selected:
            self.clear_all_btn.pack_forget()
        else:
            self.clear_all_btn.pack(side="right")
    
    def add_folder_tag(self, folder_name: str):
        """Toggle a folder in the selection"""
        # If already selected, remove it
        if folder_name in self.selected_folders_set:
            self.remove_folder_tag(folder_name, is_all=False)
            return
        
        # Otherwise add it
        if self.all_folders_selected:
            self.all_folders_selected = False
            self._refresh_selected_tags()
        
        self.selected_folders_set.add(folder_name)
        self._refresh_selected_tags()

    def remove_folder_tag(self, folder_name: str, is_all: bool = False):
        """Remove a folder from the selection"""
        if is_all:
            return
        
        self.selected_folders_set.discard(folder_name)
        
        if len(self.selected_folders_set) == 0:
            self.all_folders_selected = True
        
        self._refresh_selected_tags()

    def _refresh_selected_tags(self):
        """Refresh the selected tags display"""
        for widget in self.selected_tags_frame.winfo_children():
            widget.destroy()
        
        if self.all_folders_selected:
            self._create_selected_tag("All Folders", is_all=True)
        else:
            for folder in sorted(self.selected_folders_set):
                self._create_selected_tag(folder, is_all=False)
        
        # Update Clear All button visibility
        self._update_clear_button_visibility()
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """
        Truncate text to max_length, adding '...' if needed
        
        Args:
            text: The string to truncate
            max_length: Maximum length including the '...'
        
        Returns:
            Truncated string
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
    
    def refresh_blocks_list(self):
        """Refresh the blocks display"""
        for widget in self.blocks_frame.winfo_children():
            widget.destroy()
        
        for idx, block in enumerate(self.blocks):
            self.create_block_widget(idx, block)
    
    def create_block_widget(self, idx: int, block: SessionBlock):
        """Create a widget for a single block"""
        frame = ctk.CTkFrame(self.blocks_frame, fg_color=self.CYBER_GRAY)
        frame.pack(fill="x", pady=3, padx=5)
        
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

            folder_info = ""
            if block.folder_paths:
                # Truncate individual folder names and show max amt 3
                max_display = 3
                max_folder_length = 10
                
                truncated_folders = [
                    self._truncate_text(name, max_folder_length) 
                    for name in block.folder_paths
                ]
                
                if len(truncated_folders) <= max_display:
                    folder_info = f" [{', '.join(truncated_folders)}]"
                else:
                    shown_folders = ', '.join(truncated_folders[:max_display])
                    remaining = len(block.folder_paths) - max_display
                    folder_info = f" [{shown_folders}... +{remaining} more]"
            
            text = f"{idx + 1}. {block.count}× {duration_str}{folder_info}"
            color = self.CYBER_BLUE
        else:
            minutes = block.duration // 60
            text = f"{idx + 1}. Break {minutes}m"
            color = self.CYBER_PINK
        
        label = ctk.CTkLabel(
            frame,
            text=text,
            font=("Arial", 12),
            text_color=color,
            anchor="w"
        )
        label.pack(side="left", padx=10, pady=6, fill="x", expand=True)
        
        # Control buttons
        btn_frame = ctk.CTkFrame(frame, fg_color=self.CYBER_GRAY)
        btn_frame.pack(side="right", padx=5)
        
        # Pack delete button first
        del_btn = ctk.CTkButton(
            btn_frame,
            text="×",
            command=lambda: self.delete_block(idx),
            width=30,
            height=30,
            fg_color=self.CYBER_PINK,
            hover_color="#FF4444",
            font=("Arial", 16, "bold")
        )
        del_btn.pack(side="right", padx=2)
        
        # Down button
        if idx < len(self.blocks) - 1:
            down_btn = ctk.CTkButton(
                btn_frame,
                text="↓",
                command=lambda: self.move_block_down(idx),
                width=30,
                height=30,
                fg_color=self.CYBER_PURPLE,
                hover_color=self.CYBER_BLUE,
                font=("Arial", 14)
            )
            down_btn.pack(side="right", padx=2)
        
        # Up button
        if idx > 0:
            up_btn = ctk.CTkButton(
                btn_frame,
                text="↑",
                command=lambda: self.move_block_up(idx),
                width=30,
                height=30,
                fg_color=self.CYBER_PURPLE,
                hover_color=self.CYBER_BLUE,
                font=("Arial", 14)
            )
            up_btn.pack(side="right", padx=2)
        
        # Edit folders button
        if block.block_type == "pose":
            edit_folders_btn = ctk.CTkButton(
                btn_frame,
                text="📁",
                command=lambda: self.edit_block_folders(idx),
                width=30,
                height=30,
                fg_color=self.CYBER_TEAL,
                hover_color=self.CYBER_GREEN,
                font=("Arial", 12)
            )
            edit_folders_btn.pack(side="right", padx=2)
    
    def move_block_up(self, idx: int):
        """Move block up in the list"""
        if idx > 0:
            self.blocks[idx], self.blocks[idx - 1] = self.blocks[idx - 1], self.blocks[idx]
            self.refresh_blocks_list()
    
    def edit_block_folders(self, idx: int):
        """Open dialog to edit folders for a specific block"""
        block = self.blocks[idx]
        
        if block.block_type != "pose":
            return
        
        # Open folder selection dialog
        EditFoldersDialog(self, block, idx, self.on_block_folders_updated)
    
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
            self.duration_label.configure(text="Total: 0m")
            return
        
        total_seconds = sum(block.total_duration() for block in self.blocks)
        
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
        self.duration_label.configure(text=f"Total: {duration_str}")
    
    def show_error(self, message: str):
        """Show an error message"""
        error_label = ctk.CTkLabel(
            self.blocks_frame,
            text=f"⚠️ {message}",
            font=("Arial", 12),
            text_color="#FF4444"
        )
        error_label.pack(pady=10)
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
        
        name = self.name_entry.get().strip()
        if not name:
            name = "Custom Session"
        
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
        
        self.blocks.append(SessionBlock(block_type="pose", duration=30, count=10, folder_paths=None))
        self.blocks.append(SessionBlock(block_type="pose", duration=60, count=5, folder_paths=None))
        self.blocks.append(SessionBlock(block_type="pose", duration=300, count=2, folder_paths=None))
        self.blocks.append(SessionBlock(block_type="pose", duration=600, count=1, folder_paths=None))
        self.blocks.append(SessionBlock(block_type="break", duration=300, count=1))
        self.blocks.append(SessionBlock(block_type="pose", duration=1500, count=1, folder_paths=None))
        
        self.refresh_blocks_list()
        self.update_total_duration()
    
    def load_warmup_preset(self):
        """Load a quick warmup preset"""
        self.blocks = []
        
        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, "Quick Warmup")
        
        self.blocks.append(SessionBlock(block_type="pose", duration=15, count=20, folder_paths=None))
        self.blocks.append(SessionBlock(block_type="pose", duration=30, count=10, folder_paths=None))
        
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
        for widget in self.preset_buttons_frame.winfo_children():
            widget.destroy()
        
        ctk.CTkButton(
            self.preset_buttons_frame,
            text="📚 1Hr Class",
            command=self.load_1hr_class_preset,
            font=("Arial", 10),
            fg_color=self.CYBER_PURPLE,
            hover_color=self.CYBER_BLUE,
            text_color="#FFFFFF",
            width=100,
            height=28
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            self.preset_buttons_frame,
            text="🔥 Warmup",
            command=self.load_warmup_preset,
            font=("Arial", 10),
            fg_color=self.CYBER_PINK,
            hover_color=self.CYBER_PURPLE,
            text_color="#FFFFFF",
            width=100,
            height=28
        ).pack(side="left", padx=2)
        
        if self.custom_presets:
            for preset_name in self.custom_presets.keys():
                ctk.CTkButton(
                    self.preset_buttons_frame,
                    text=f"⭐ {preset_name}",
                    command=lambda name=preset_name: self.load_custom_preset(name),
                    font=("Arial", 10),
                    fg_color=self.CYBER_GREEN,
                    hover_color=self.CYBER_TEAL,
                    text_color="#000000",
                    width=120,
                    height=28
                ).pack(side="left", padx=2)
    
    def load_custom_preset(self, preset_name: str):
        """Load a custom preset by name with folder validation"""
        if preset_name not in self.custom_presets:
            return
        
        preset_data = self.custom_presets[preset_name]
        
        self.blocks = []
        
        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, preset_name)
        
        # Get current available folders for validation
        available_folders = set(self.get_available_folders())
        
        for block_data in preset_data['blocks']:
            folder_paths = block_data.get('folder_paths')
            
            # Validate folders if they exist
            if folder_paths:
                valid_folders = [f for f in folder_paths if f in available_folders]
                
                if len(valid_folders) == 0:
                    folder_paths = None
                else:
                    folder_paths = valid_folders
            
            self.blocks.append(
                SessionBlock(
                    block_type=block_data['block_type'],
                    duration=block_data['duration'],
                    count=block_data['count'],
                    folder_paths=folder_paths
                )
            )
        
        self.refresh_blocks_list()
        self.update_total_duration()
    
    def save_as_preset(self):
        """Save current session configuration as a preset"""
        if not self.blocks:
            self.show_error("Please add at least one block before saving!")
            return
        
        # Get session name from input field
        session_name = self.name_entry.get().strip()
        
        # Open custom save dialog with session name prefilled
        SavePresetDialog(self, self.blocks, self.on_preset_saved, default_name=session_name)
    
    def on_preset_saved(self, preset_name: str, preset_data: dict):
        """Callback when preset is saved from dialog"""
        self.custom_presets[preset_name] = preset_data
        self.save_presets()
        self.refresh_preset_buttons()
        
        # Show confirmation
        confirm_label = ctk.CTkLabel(
            self.preset_buttons_frame,
            text=f"✅ Saved!",
            font=("Arial", 10, "bold"),
            text_color=self.CYBER_GREEN
        )
        confirm_label.pack(side="left", padx=5)
        self.after(2000, confirm_label.destroy)
    
    def open_manage_presets(self):
        """Open preset management dialog"""
        ManagePresetsDialog(self, self.custom_presets, self.on_presets_updated)
    
    def on_presets_updated(self, updated_presets: dict):
        """Called when presets are modified in manage dialog"""
        self.custom_presets = updated_presets
        self.save_presets()
        self.refresh_preset_buttons()
    
    def on_block_folders_updated(self, block_idx: int, new_folder_paths: Optional[List[str]]):
        """Called when block folders are updated from edit dialog"""
        if 0 <= block_idx < len(self.blocks):
            self.blocks[block_idx].folder_paths = new_folder_paths
            self.refresh_blocks_list()

class SavePresetDialog(ctk.CTkToplevel):
    """Dialog for saving presets with options"""
    
    def __init__(self, parent, blocks: List[SessionBlock], on_save_callback, default_name: str = ""):
        super().__init__(parent)
        
        self.blocks = blocks
        self.on_save_callback = on_save_callback
        self.default_name = default_name if default_name else ""
        
        # Dialog setup
        self.title("Save Preset")
        self.geometry("450x480")
        self.resizable(False, False)
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        
        dialog_width = 450
        dialog_height = 480
        
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        if x < 0:
            x = 20
        if x + dialog_width > screen_width:
            x = screen_width - dialog_width - 20
        if y < 0:
            y = 20
        if y + dialog_height > screen_height:
            y = screen_height - dialog_height - 20
        
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Colors
        self.CYBER_PINK = "#FF6EC7"
        self.CYBER_PURPLE = "#8B5CF6"
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
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Header
        header = ctk.CTkLabel(
            main_frame,
            text="Save as Preset",
            font=("Arial", 18, "bold"),
            text_color=self.CYBER_BLUE
        )
        header.pack(pady=(0, 20))
        
        # Preset name
        name_label = ctk.CTkLabel(
            main_frame,
            text="Preset Name:",
            font=("Arial", 13, "bold"),
            text_color=self.CYBER_TEXT,
            anchor="w"
        )
        name_label.pack(fill="x", pady=(0, 5))
        
        self.name_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="My Custom Preset",
            font=("Arial", 13),
            height=35
        )
        self.name_entry.pack(fill="x", pady=(0, 25))
        
        # Set default name if provided
        if self.default_name:
            self.name_entry.insert(0, self.default_name)
        
        # Options
        options_label = ctk.CTkLabel(
            main_frame,
            text="Save Options:",
            font=("Arial", 13, "bold"),
            text_color=self.CYBER_TEXT,
            anchor="w"
        )
        options_label.pack(fill="x", pady=(0, 10))
        
        self.save_option = ctk.StringVar(value="with_folders")
        
        # Save w/ folders
        option1_frame = ctk.CTkFrame(main_frame, fg_color=self.CYBER_GRAY, corner_radius=8)
        option1_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkRadioButton(
            option1_frame,
            text="Save with folder selections",
            variable=self.save_option,
            value="with_folders",
            font=("Arial", 12),
            fg_color=self.CYBER_BLUE,
            hover_color=self.CYBER_PURPLE
        ).pack(anchor="w", padx=15, pady=10)
        
        ctk.CTkLabel(
            option1_frame,
            text="Preserves which folders each block uses",
            font=("Arial", 10),
            text_color=self.CYBER_TEXT
        ).pack(anchor="w", padx=35, pady=(0, 10))
        
        # Save without folders
        option2_frame = ctk.CTkFrame(main_frame, fg_color=self.CYBER_GRAY, corner_radius=8)
        option2_frame.pack(fill="x", pady=(0, 25))
        
        ctk.CTkRadioButton(
            option2_frame,
            text="Save without folder selections",
            variable=self.save_option,
            value="without_folders",
            font=("Arial", 12),
            fg_color=self.CYBER_PINK,
            hover_color=self.CYBER_PURPLE
        ).pack(anchor="w", padx=15, pady=10)
        
        ctk.CTkLabel(
            option2_frame,
            text="All blocks will use 'All Folders' (universal preset)",
            font=("Arial", 10),
            text_color=self.CYBER_TEXT
        ).pack(anchor="w", padx=35, pady=(0, 10))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color=self.CYBER_DARK)
        button_frame.pack(fill="x")
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel,
            font=("Arial", 12),
            fg_color=self.CYBER_GRAY,
            hover_color=self.CYBER_LIGHT_GRAY,
            width=100,
            height=35
        )
        cancel_btn.pack(side="left")
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Preset",
            command=self.save,
            font=("Arial", 12, "bold"),
            fg_color=self.CYBER_GREEN,
            hover_color=self.CYBER_BLUE,
            text_color="#000000",
            width=140,
            height=35
        )
        save_btn.pack(side="right")
    
    def cancel(self):
        """Cancel without saving"""
        self.grab_release()
        self.destroy()
    
    def save(self):
        """Save preset with chosen option"""
        preset_name = self.name_entry.get().strip()
        
        if not preset_name:
            # Flash the entry to indicate error
            self.name_entry.configure(border_color="#FF4444")
            self.after(500, lambda: self.name_entry.configure(border_color=""))
            return
        
        save_with_folders = (self.save_option.get() == "with_folders")
        
        # Build preset data
        preset_data = {
            'blocks': [
                {
                    'block_type': block.block_type,
                    'duration': block.duration,
                    'count': block.count,
                    'folder_paths': block.folder_paths if save_with_folders else None
                }
                for block in self.blocks
            ]
        }
        
        self.on_save_callback(preset_name, preset_data)
        self.grab_release()
        self.destroy()


class EditFoldersDialog(ctk.CTkToplevel):
    """Dialog for editing folders for a specific block"""
    
    def __init__(self, parent, block: SessionBlock, block_idx: int, on_update_callback):
        super().__init__(parent)
        
        self.block = block
        self.block_idx = block_idx
        self.on_update_callback = on_update_callback
        self.parent_window = parent
        
        # Dialog setup
        self.title(f"Edit Folders - Block {block_idx + 1}")
        self.geometry("500x650")
        self.resizable(False, False)
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        
        # Position over right column of parent
        self.update_idletasks()
        
        dialog_width = 500
        dialog_height = 650
        
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Position dialog to overlap the right side of parent
        left_column_width = 500
        x = parent_x + left_column_width + 20
        y = parent_y + (parent_height - dialog_height) // 2
        
        # Keep within screen bounds
        if x + dialog_width > screen_width:
            x = screen_width - dialog_width - 20
        
        if y < 20:
            y = 20
        if y + dialog_height > screen_height:
            y = screen_height - dialog_height - 20
        
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Colors
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
        
        # Initialize selection state from block
        if block.folder_paths is None:
            self.all_folders_selected = True
            self.selected_folders_set = set()
        else:
            self.all_folders_selected = False
            self.selected_folders_set = set(block.folder_paths)
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ctk.CTkFrame(self, fg_color=self.CYBER_DARK)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkLabel(
            main_frame,
            text=f"Select Folders for Block {self.block_idx + 1}",
            font=("Arial", 16, "bold"),
            text_color=self.CYBER_BLUE
        )
        header.pack(pady=(0, 10))
        
        # Info
        info = ctk.CTkLabel(
            main_frame,
            text=f"{self.block.count}× {self.block.duration}s poses",
            font=("Arial", 12),
            text_color=self.CYBER_TEXT
        )
        info.pack(pady=(0, 20))
        
        # Folders section
        folders_frame = ctk.CTkFrame(main_frame, fg_color=self.CYBER_GRAY, corner_radius=10)
        folders_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Header with Clear All
        folders_header = ctk.CTkFrame(folders_frame, fg_color=self.CYBER_GRAY)
        folders_header.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            folders_header,
            text="Folders:",
            font=("Arial", 13, "bold"),
            text_color=self.CYBER_PURPLE
        ).pack(side="left")
        
        self.clear_all_btn = ctk.CTkButton(
            folders_header,
            text="Clear All",
            command=self.clear_all_folders,
            font=("Arial", 10),
            fg_color=self.CYBER_PINK,
            hover_color="#FF4444",
            text_color="#FFFFFF",
            width=70,
            height=22
        )
        
        # Selected tags, scrollable
        selected_tags_container = ctk.CTkFrame(
            folders_frame,
            fg_color=self.CYBER_GRAY,
            height=70
        )
        selected_tags_container.pack(fill="x", padx=15, pady=(0, 10))
        selected_tags_container.pack_propagate(False)
        
        self.selected_tags_frame = ctk.CTkScrollableFrame(
            selected_tags_container,
            fg_color=self.CYBER_LIGHT_GRAY,
            orientation="horizontal"
        )
        self.selected_tags_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        self._refresh_selected_tags()
        
        # Search bar
        search_frame = ctk.CTkFrame(folders_frame, fg_color=self.CYBER_GRAY)
        search_frame.pack(fill="x", padx=15, pady=(0, 5))
        
        ctk.CTkLabel(
            search_frame,
            text="🔍",
            font=("Arial", 12),
            text_color=self.CYBER_TEXT
        ).pack(side="left", padx=(0, 5))
        
        self.folder_search_var = ctk.StringVar()
        self.folder_search_var.trace_add("write", self._on_search_changed)
        
        self.folder_search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search folders...",
            font=("Arial", 11),
            textvariable=self.folder_search_var,
            height=28
        )
        self.folder_search_entry.pack(side="left", fill="x", expand=True)
        
        # Available folders
        available_scroll = ctk.CTkScrollableFrame(
            folders_frame,
            fg_color=self.CYBER_DARK,
            height=280
        )
        available_scroll.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        
        self.available_container = ctk.CTkFrame(available_scroll, fg_color=self.CYBER_DARK)
        self.available_container.pack(fill="x", expand=True)
        
        # Get available folders from parent
        self.available_folders = self.parent_window.get_available_folders()
        self.folder_buttons = {}
        
        self._create_folder_buttons()
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color=self.CYBER_DARK)
        button_frame.pack(fill="x")
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel,
            font=("Arial", 12),
            fg_color=self.CYBER_GRAY,
            hover_color=self.CYBER_LIGHT_GRAY,
            width=100,
            height=35
        )
        cancel_btn.pack(side="left", padx=(0, 10))
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save,
            font=("Arial", 12, "bold"),
            fg_color=self.CYBER_GREEN,
            hover_color=self.CYBER_TEAL,
            text_color="#000000",
            width=120,
            height=35
        )
        save_btn.pack(side="right")
    
    def _create_folder_buttons(self, filter_text: str = ""):
        """Create folder buttons with optional filtering"""
        for widget in self.available_container.winfo_children():
            widget.destroy()
        self.folder_buttons.clear()
        
        filtered_folders = [
            f for f in self.available_folders 
            if filter_text.lower() in f.lower()
        ]
        
        # Sort alphabetically (case-insensitive)
        filtered_folders.sort(key=str.lower)
        
        if not filtered_folders:
            no_results = ctk.CTkLabel(
                self.available_container,
                text="No folders match search",
                font=("Arial", 11),
                text_color=self.CYBER_TEXT
            )
            no_results.grid(row=0, column=0, columnspan=2, pady=20)
            return
        
        tags_per_row = 2
        for idx, folder in enumerate(filtered_folders):
            row = idx // tags_per_row
            col = idx % tags_per_row
            
            tag_btn = ctk.CTkButton(
                self.available_container,
                text=folder,
                font=("Arial", 10),
                fg_color=self.CYBER_PURPLE,
                hover_color=self.CYBER_BLUE,
                text_color="#FFFFFF",
                height=26,
                corner_radius=13,
                command=lambda f=folder: self.add_folder_tag(f)
            )
            tag_btn.grid(row=row, column=col, padx=4, pady=4, sticky="ew")
            self.folder_buttons[folder] = tag_btn
        
        self.available_container.grid_columnconfigure(0, weight=1)
        self.available_container.grid_columnconfigure(1, weight=1)
    
    def _on_search_changed(self, *args):
        """Called when search text changes"""
        search_text = self.folder_search_var.get()
        self._create_folder_buttons(search_text)
    
    def clear_all_folders(self):
        """Clear all selected folders"""
        self.selected_folders_set.clear()
        self.all_folders_selected = True
        self._refresh_selected_tags()
    
    def add_folder_tag(self, folder_name: str):
        """Toggle a folder in the selection"""
        # If already selected, remove it
        if folder_name in self.selected_folders_set:
            self.remove_folder_tag(folder_name, is_all=False)
            return
        
        # Otherwise add it
        if self.all_folders_selected:
            self.all_folders_selected = False
            self._refresh_selected_tags()
        
        self.selected_folders_set.add(folder_name)
        self._refresh_selected_tags()
    
    def remove_folder_tag(self, folder_name: str, is_all: bool = False):
        """Remove a folder from the selection"""
        if is_all:
            return
        
        self.selected_folders_set.discard(folder_name)
        
        if len(self.selected_folders_set) == 0:
            self.all_folders_selected = True
        
        self._refresh_selected_tags()
    
    def _refresh_selected_tags(self):
        """Refresh the selected tags display"""
        for widget in self.selected_tags_frame.winfo_children():
            widget.destroy()
        
        if self.all_folders_selected:
            self._create_selected_tag("All Folders", is_all=True)
        else:
            for folder in sorted(self.selected_folders_set):
                self._create_selected_tag(folder, is_all=False)
        
        self._update_clear_button_visibility()
    
    def _create_selected_tag(self, folder_name: str, is_all: bool = False):
        """Create a selected tag pill"""
        tag_frame = ctk.CTkFrame(
            self.selected_tags_frame,
            fg_color=self.CYBER_PINK if is_all else self.CYBER_PURPLE,
            corner_radius=12,
            height=25
        )
        tag_frame.pack(side="left", padx=3, pady=5)
        
        ctk.CTkLabel(
            tag_frame,
            text=folder_name,
            font=("Arial", 10, "bold" if is_all else "normal"),
            text_color="#FFFFFF"
        ).pack(side="left", padx=(8, 4), pady=2)
        
        if not is_all or len(self.selected_folders_set) > 0:
            x_btn = ctk.CTkButton(
                tag_frame,
                text="×",
                font=("Arial", 14, "bold"),
                fg_color="transparent",
                hover_color=self.CYBER_DARK,
                text_color="#FFFFFF",
                width=20,
                height=20,
                command=lambda: self.remove_folder_tag(folder_name, is_all)
            )
            x_btn.pack(side="left", padx=(0, 4), pady=2)
    
    def _update_clear_button_visibility(self):
        """Show/hide Clear All button"""
        if self.all_folders_selected:
            self.clear_all_btn.pack_forget()
        else:
            self.clear_all_btn.pack(side="right")
    
    def cancel(self):
        """Cancel without saving"""
        self.grab_release()
        self.destroy()
    
    def save(self):
        """Save folder selection and close"""
        if self.all_folders_selected:
            new_folder_paths = None
        else:
            new_folder_paths = sorted(list(self.selected_folders_set)) if self.selected_folders_set else None
        
        self.on_update_callback(self.block_idx, new_folder_paths)
        self.grab_release()
        self.destroy()


class ManagePresetsDialog(ctk.CTkToplevel):
    """Dialog for managing saved presets"""
    
    def __init__(self, parent, presets: dict, on_update_callback):
        super().__init__(parent)
        
        self.presets = presets.copy()
        self.on_update_callback = on_update_callback
        
        self.title("Manage Presets")
        self.geometry("500x400")
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        
        self.update_idletasks()
        
        dialog_width = 500
        dialog_height = 400

        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        if x < 0:
            x = 20
        if x + dialog_width > screen_width:
            x = screen_width - dialog_width - 20
        if y < 0:
            y = 20
        if y + dialog_height > screen_height:
            y = screen_height - dialog_height - 20
        
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
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
        
        info = ctk.CTkLabel(
            main_frame,
            text="Built-in presets (1 Hr Class Mode, Quick Warmup) cannot be deleted.",
            font=("Arial", 11),
            text_color=self.CYBER_TEXT,
            wraplength=450
        )
        info.pack(pady=(0, 15))
        
        self.preset_list_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color=self.CYBER_LIGHT_GRAY,
            height=200
        )
        self.preset_list_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        self.refresh_preset_list()
        
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