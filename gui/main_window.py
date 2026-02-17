import sys
from pathlib import Path
import threading
import os

# Get base path for resources (works with PyInstaller)
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import customtkinter as ctk
from PIL import Image, ImageTk
from typing import Optional

from models.session import Session, SessionBlock
from models.image_collection import ImageCollection
from controllers.session_controller import SessionController, SessionState
from controllers.keyboard_shortcuts import KeyboardShortcutsManager
from gui.session_builder import SessionBuilderDialog
from gui.settings_dialog import SettingsDialog
from theme_config import get_theme, load_current_theme, get_canvas_bg


class MainWindow(ctk.CTk):
    def get_reference_folder_path(self):
        """Get reference folder path from settings or prompt user to choose"""
        import json
        from tkinter import filedialog, messagebox
        
        settings_file = Path("settings/app_settings.json")
        
        # Try to load from settings
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    ref_path = Path(settings.get('reference_folder', ''))
                    if ref_path.exists():
                        return ref_path
            except:
                pass
        
        # Prompt user to choose folder
        messagebox.showinfo(
            "Select Reference Folder",
            "Welcome to CroquisCadence!\n\n"
            "Please select the folder containing your reference images.\n\n"
            "You can organize images into subfolders (e.g., 'hands', 'poses', 'anatomy')."
        )
        
        folder = filedialog.askdirectory(
            title="Select Reference Images Folder",
            mustexist=True
        )
        
        if not folder:
            return None  # User cancelled
        
        ref_path = Path(folder)
        
        # Save to settings
        settings_file.parent.mkdir(exist_ok=True)
        settings = {'reference_folder': str(ref_path)}
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        
        return ref_path
    
    def __init__(self):
        super().__init__()
        
        # Load theme
        self.current_theme_name = load_current_theme()
        self.theme = get_theme(self.current_theme_name)
        
        # Calculate smart text colors for buttons
        from theme_config import get_text_color_for_bg
        self.text_for_primary = get_text_color_for_bg(self.theme["primary"])
        self.text_for_secondary = get_text_color_for_bg(self.theme["secondary"])
        self.text_for_accent = get_text_color_for_bg(self.theme["accent"])
        self.text_for_success = get_text_color_for_bg(self.theme["success"])
        
        self.title("CroquisCadence")
        self.geometry("1400x800")
        self.resizable(True, True)
        self.configure(fg_color=self.theme["dark"])
        
        # Set window icon
        try:
            icon_path = resource_path("assets/icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except:
            pass  # Icon is optional, continue without it

        ctk.set_appearance_mode("dark")
        
        # Get reference folder path from settings or prompt user
        reference_path = self.get_reference_folder_path()
        if not reference_path:
            # User cancelled or no path - exit
            self.destroy()
            return
        
        # Initialize controllers
        self.image_collection = ImageCollection(reference_path)
        self.session_controller = SessionController(self.image_collection)
        self.shortcuts_manager = KeyboardShortcutsManager()
        
        # Register session callbacks
        self.session_controller.on_new_block = self.handle_new_block
        self.session_controller.on_tick = self.handle_tick
        self.session_controller.on_session_end = self.handle_session_end
        self.session_controller.on_image_change = self.handle_image_change
        
        # Register keyboard shortcut callbacks
        self.setup_keyboard_shortcuts()
        
        # State
        self.current_image_path: Optional[Path] = None
        self.is_fullscreen = False
        
        # Image caching
        self._image_cache = {}

        # Resize debouncing
        self._resize_timer = None
        
        self.create_widgets()
        
        self.break_image = Image.open(resource_path("assets/break_image.jpg"))

        self.bind("<Configure>", self.on_window_resize)
        
        self.bind("<Escape>", self.exit_fullscreen)
        
        self.bind_keyboard_shortcuts()

        # Store current image path for resizing
        self.current_displayed_image: Optional[Path] = None
        
    
    def _update_nsfw_badge(self, image_path):
        """Update the NSFW/SFW badge based on the current image filename"""
        if image_path is None:
            self.nsfw_badge_label.configure(text="", fg_color="transparent")
            return

        from models.image_collection import is_nsfw_image
        if is_nsfw_image(image_path):
            self.nsfw_badge_label.configure(
                text="NSFW",
                fg_color="#CC2222",
                text_color="#FFFFFF"
            )
        else:
            self.nsfw_badge_label.configure(
                text="SFW",
                fg_color="#22AA44",
                text_color="#FFFFFF"
            )

    def _disable_button(self, button):
        """Grey out a button to show it's inactive (keeps layout stable, no shifting)"""
        bg = self.theme["gray"]
        button.configure(
            state="disabled",
            fg_color=bg,
            hover_color=bg,
            text_color="#555555",
            border_width=1,
            border_color="#444444"
        )

    def _show_button(self, button, fg_color, hover_color, text_color, border_width=0, border_color=None):
        """Make a previously hidden button visible again"""
        config = dict(
            state="normal",
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            border_width=border_width
        )
        if border_color:
            config["border_color"] = border_color
        button.configure(**config)

    def setup_keyboard_shortcuts(self):
        """Register callbacks for keyboard shortcuts"""
        self.shortcuts_manager.register_callback("pause_resume", self.toggle_pause)
        self.shortcuts_manager.register_callback("previous_image", self.previous_image)
        self.shortcuts_manager.register_callback("next_image", self.next_image)
        self.shortcuts_manager.register_callback("previous_block", self.previous_block)
        self.shortcuts_manager.register_callback("next_block", self.next_block_actual)
    
    def bind_keyboard_shortcuts(self):
        """Bind all keyboard shortcuts to the window"""
        # Get all shortcuts and bind them
        for action, binding in self.shortcuts_manager.get_all_shortcuts().items():
            for key in binding.get_all_keys():
                self.bind(f"<{key}>", lambda e, k=key: self.handle_shortcut(k))
    
    def handle_shortcut(self, key: str):
        """Handle keyboard shortcut press"""
        # Only handle shortcuts when session is running or paused
        if self.session_controller.state in [SessionState.RUNNING, SessionState.PAUSED]:
            self.shortcuts_manager.handle_key_press(key)

    def on_window_resize(self, event):
        """Handle window resize - rescale current image with debouncing"""
        # Cancel previous timer if it exists
        if self._resize_timer is not None:
            self.after_cancel(self._resize_timer)
        
        # Schedule redraw after 150ms of no resize events
        self._resize_timer = self.after(150, self._do_resize)
    
    def _do_resize(self):
        """Actually perform the resize after debounce delay"""
        self._resize_timer = None
        
        # Only resize if have an image displayed
        if self.current_displayed_image and self.session_controller.state != SessionState.IDLE:
            # Check if break or pose
            current_block = self.session_controller.session.blocks[self.session_controller.current_block_index]
            if current_block.block_type == "pose":
                self.display_image(self.current_displayed_image)
            else:
                self.display_break()

    def previous_image(self):
        """Show previous image for current block, skip breaks"""
        # Fixes NoneType object has no attribute "blocks" error
        if not self.session_controller.session:
            return
        
        # Check if current block is a break
        current_block = self.session_controller.session.blocks[self.session_controller.current_block_index]
        
        if current_block.block_type == "break":
            # On a break, go to previous block instead
            self.session_controller.skip_to_previous_block()
        else:
            self.session_controller.previous_image()

    def next_image(self):
        """Show next image for current block, skip breaks"""
        if not self.session_controller.session:
            return
        # Check if current block is a break
        current_block = self.session_controller.session.blocks[self.session_controller.current_block_index]
        
        if current_block.block_type == "break":
            # On a break, go to next block instead
            self.session_controller.skip_to_next_block()
        else:
            self.session_controller.next_image()

    def previous_block(self):
        """Go to previous block"""
        self.session_controller.skip_to_previous_block()

    def next_block_actual(self):
        """Go to next block"""
        self.session_controller.skip_to_next_block()
            
    def create_widgets(self):
        """Create all GUI widgets"""
        t = self.theme
        CYBER_PINK   = t["primary"]
        CYBER_PURPLE = t["accent"]
        CYBER_BLUE   = t["secondary"]
        CYBER_GREEN  = t["success"]
        CYBER_DARK   = t["dark"]
        CYBER_GRAY   = t["gray"]
        CYBER_TEXT   = t["text"]
        
        self.main_container = ctk.CTkFrame(self, fg_color=CYBER_DARK)
        self.main_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Top accent bar (matcha green theme accent)
        top_accent = ctk.CTkFrame(
            self.main_container,
            fg_color=CYBER_PINK,  # Primary theme color
            height=6,
            corner_radius=0
        )
        top_accent.pack(fill="x", side="top", padx=0, pady=0)

        # Minimal progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.main_container,
            height=4,
            corner_radius=0,
            progress_color=CYBER_BLUE,
            fg_color=t["light_gray"]
        )
        self.progress_bar.pack(fill="x", side="bottom", padx=0, pady=(0, 0))
        self.progress_bar.set(0)

        # Info/controls bar
        self.info_bar = ctk.CTkFrame(self.main_container, fg_color=CYBER_GRAY, height=100)
        self.info_bar.pack(fill="x", side="bottom", padx=20, pady=20)
        self.info_bar.pack_propagate(False)

        # Left info frame - anchored to left edge, fixed size, never pushes center
        left_info_frame = ctk.CTkFrame(self.info_bar, fg_color=CYBER_GRAY)
        left_info_frame.place(relx=0.0, rely=0.5, anchor="w", x=20)
        left_info_frame.configure(width=350, height=60)
        left_info_frame.pack_propagate(False)

        # Block info - top line
        self.block_info_label = ctk.CTkLabel(
            left_info_frame,
            text="Ready to start",
            font=("Arial", 16),
            text_color=CYBER_BLUE,
            anchor="w",
            width=340
        )
        self.block_info_label.pack(anchor="w")

        # Folder tag row - second line, folder name + nsfw badge side by side
        folder_tag_row = ctk.CTkFrame(left_info_frame, fg_color=CYBER_GRAY)
        folder_tag_row.pack(anchor="w")

        self.folder_tag_label = ctk.CTkLabel(
            folder_tag_row,
            text="",
            font=("Arial", 11),
            text_color=CYBER_PURPLE,
            anchor="w"
        )
        self.folder_tag_label.pack(side="left")

        self.nsfw_badge_label = ctk.CTkLabel(
            folder_tag_row,
            text="",
            font=("Arial", 10, "bold"),
            corner_radius=4,
            width=0
        )
        self.nsfw_badge_label.pack(side="left", padx=(6, 0))

        # Timer and history frame - anchored to right edge, fixed size
        timer_frame = ctk.CTkFrame(self.info_bar, fg_color=CYBER_GRAY)
        timer_frame.place(relx=1.0, rely=0.5, anchor="e", x=-20)

        # Timer
        self.timer_label = ctk.CTkLabel(
            timer_frame,
            text="00:00",
            font=("Arial", 32, "bold"),
            text_color=CYBER_PINK
        )
        self.timer_label.pack(side="left", padx=(0, 10))
        
        # Image history button
        self.history_button = ctk.CTkButton(
            timer_frame,
            text="📜",
            command=self.show_image_history,
            width=45,
            height=45,
            font=("Arial", 20),
            fg_color=CYBER_PURPLE,
            hover_color=CYBER_PINK,
            corner_radius=8
        )
        self.history_button.pack(side="left")
        self._disable_button(self.history_button)  # Disabled by default, enabled during session

        # Control buttons - use place() to anchor dead center, immune to left/right content changing
        self.button_frame = ctk.CTkFrame(self.info_bar, fg_color=CYBER_GRAY)
        self.button_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Start button
        self.start_button = ctk.CTkButton(
            self.button_frame,
            text="▶ START",
            command=self.open_session_builder,
            width=100,
            fg_color=CYBER_GREEN,
            hover_color=CYBER_GREEN,
            text_color=self.text_for_success,
            font=("Arial", 13, "bold")
        )
        self.start_button.pack(side="left", padx=5)

        # Previous block button
        self.prev_block_button = ctk.CTkButton(
            self.button_frame,
            text="⏮",
            command=self.previous_block,
            width=60,
            fg_color=CYBER_PURPLE,
            hover_color=CYBER_PURPLE,
            text_color=self.text_for_accent,
            font=("Arial", 20)
        )
        self.prev_block_button.pack(side="left", padx=5)

        # Previous image button
        self.prev_image_button = ctk.CTkButton(
            self.button_frame,
            text="◀",
            command=self.previous_image,
            width=60,
            fg_color=CYBER_BLUE,
            hover_color=CYBER_BLUE,
            text_color=self.text_for_secondary,
            font=("Arial", 20, "bold")
        )
        self.prev_image_button.pack(side="left", padx=5)

        # Pause button
        self.pause_button = ctk.CTkButton(
            self.button_frame,
            text="⏸",
            command=self.toggle_pause,
            width=60,
            fg_color=CYBER_PINK,
            hover_color=CYBER_PINK,
            text_color=self.text_for_primary,
            font=("Arial", 22, "bold")
        )
        self.pause_button.pack(side="left", padx=5)

        # Next image button
        self.next_image_button = ctk.CTkButton(
            self.button_frame,
            text="▶",
            command=self.next_image,
            width=60,
            fg_color=CYBER_BLUE,
            hover_color=CYBER_BLUE,
            text_color=self.text_for_secondary,
            font=("Arial", 20, "bold")
        )
        self.next_image_button.pack(side="left", padx=5)

        # Next block button
        self.next_block_button = ctk.CTkButton(
            self.button_frame,
            text="⏭",
            command=self.next_block_actual,
            width=60,
            fg_color=CYBER_PURPLE,
            hover_color=CYBER_PURPLE,
            text_color=self.text_for_accent,
            font=("Arial", 20)
        )
        self.next_block_button.pack(side="left", padx=5)

        # Stop button
        self.stop_button = ctk.CTkButton(
            self.button_frame,
            text="⏹ END SESSION",
            command=self.stop_session,
            width=140,
            fg_color=CYBER_PINK,
            hover_color=CYBER_PINK,
            text_color=self.text_for_primary,
            font=("Arial", 13, "bold")
        )
        self.stop_button.pack(side="left", padx=5)
        self._disable_button(self.stop_button)  # Disabled until session starts
        self.settings_button = ctk.CTkButton(
            self.button_frame,
            text="⚙",
            command=self.open_settings,
            width=60,
            fg_color=CYBER_GRAY,
            hover_color=CYBER_PURPLE,
            border_width=2,
            border_color=CYBER_BLUE,
            text_color=CYBER_TEXT,
            font=("Arial", 18)
        )
        self.settings_button.pack(side="left", padx=5)

        # Pin button (Always on Top)
        self.is_pinned = False
        self.pin_button = ctk.CTkButton(
            self.button_frame,
            text="📌",
            command=self.toggle_always_on_top,
            width=60,
            fg_color=CYBER_GRAY,
            hover_color=CYBER_PURPLE,
            border_width=2,
            border_color=CYBER_BLUE,
            text_color=CYBER_TEXT,
            font=("Arial", 18)
        )
        self.pin_button.pack(side="left", padx=5)

        # Image display area
        self.image_frame = ctk.CTkFrame(self.main_container, fg_color=CYBER_DARK)
        self.image_frame.pack(fill="both", expand=True, padx=5, pady=(5, 0))

        # Use Canvas instead of Label
        import tkinter as tk
        self.image_canvas = tk.Canvas(
            self.image_frame,
            bg=get_canvas_bg(self.theme),
            highlightthickness=0,
            bd=0
        )
        self.image_canvas.pack(fill="both", expand=True)
        
        # Bind right-click for image tagging
        self.image_canvas.bind("<Button-3>", self.show_image_context_menu)
        
        # Store canvas image reference (must keep ref to prevent garbage collection)
        self.canvas_image_ref = None
        self.current_image_path = None  # Track current image for tagging
    
    def handle_new_block(self, block_index, block, image_path, is_auto=False):
        """Called when a new block starts
        
        Args:
            block_index: Index of the new block
            block: The SessionBlock object
            image_path: Path to the image to display
            is_auto: True if block changed automatically (timer), False if manual (button)
        """
        # Force UI to update immediately so controls are responsive
        self.update_idletasks()
        
        # Play transition sound ONLY for automatic block transitions
        if is_auto and block_index > 0:
            self.play_transition_sound()

        total_blocks = len(self.session_controller.session.blocks)
        
        current_duration = block.duration
        remaining_same_duration = 0
        
        # Count CONSECUTIVE blocks from current onwards (stop at breaks, different duration, folders, or filter)
        for i in range(block_index, total_blocks):
            check_block = self.session_controller.session.blocks[i]
            
            if (check_block.block_type == block.block_type
                    and check_block.duration == current_duration
                    and check_block.folder_paths == block.folder_paths
                    and check_block.nsfw_filter == block.nsfw_filter):
                remaining_same_duration += 1
            else:
                break
        
        # Format the block info text
        if block.block_type == "pose":
            if current_duration < 60:
                duration_str = f"{current_duration}s"
            elif current_duration < 3600:
                minutes = current_duration // 60
                duration_str = f"{minutes}m"
            else:
                hours = current_duration // 3600
                minutes = (current_duration % 3600) // 60
                if minutes > 0:
                    duration_str = f"{hours}h {minutes}m"
                else:
                    duration_str = f"{hours}h"
            
            # Show remaining count
            if remaining_same_duration > 1:
                block_text = f"{remaining_same_duration} more of this type, {duration_str} each"
            else:
                block_text = f"Last {duration_str} pose"
        else:
            minutes = current_duration // 60
            block_text = f"Break - {minutes}m"
        
        self.block_info_label.configure(text=block_text)

        # Update timer display to show the full block duration
        minutes = block.duration // 60
        seconds = block.duration % 60
        time_text = f"{minutes:02d}:{seconds:02d}"
        self.timer_label.configure(text=time_text, text_color=self.theme.get("timer_normal", self.theme.get("timer", self.theme["primary"])))
        
        # Reset warning tracking for new block
        self._triggered_warnings = set()

        # Update progress bar
        self.update_progress()

        if block.block_type == "pose" and image_path:
            self.display_image(image_path)
            
            # Extract and display folder name + nsfw badge
            try:
                folder_name = image_path.parent.name
                self.folder_tag_label.configure(text=f"📁 {folder_name}")
            except:
                self.folder_tag_label.configure(text="")
            self._update_nsfw_badge(image_path)
        else:
            self.display_break()
            self.folder_tag_label.configure(text="")
            self._update_nsfw_badge(None)
    
    def handle_image_change(self, image_path):
        """Called when image changes within the same block (timer should NOT reset)"""
        if image_path:
            self.display_image(image_path)
            try:
                folder_name = image_path.parent.name
                self.folder_tag_label.configure(text=f"📁 {folder_name}")
            except:
                pass
            self._update_nsfw_badge(image_path)
        
    def handle_tick(self, remaining):
        """Called every second during countdown"""
        # Update timer display
        minutes = remaining // 60
        seconds = remaining % 60
        time_text = f"{minutes:02d}:{seconds:02d}"
        
        # Calculate warning threshold based on block duration
        current_block = self.session_controller.session.blocks[self.session_controller.current_block_index]
        block_duration = current_block.duration
        
        # Load custom warnings
        from theme_config import load_warnings
        warnings = load_warnings()
        
        # Sort warnings by percentage (highest first) so check from most urgent to least
        sorted_warnings = sorted(warnings, key=lambda w: w['percentage'])
        
        # Determine which warning level in
        current_percentage = (remaining / block_duration) * 100
        
        # Find the appropriate warning
        triggered_warning = None
        for warning in sorted_warnings:
            if current_percentage <= warning['percentage']:
                triggered_warning = warning
                break
        
        # Set timer color and play sound if entered a new warning zone
        if triggered_warning:
            # Get color - use custom color_hex if set, otherwise use theme color
            if 'color_hex' in triggered_warning and triggered_warning['color_hex']:
                warning_color = triggered_warning['color_hex']
            else:
                warning_color = self.theme.get(triggered_warning.get('color', 'timer_warning_10'), self.theme.get("timer", self.theme["primary"]))
            
            self.timer_label.configure(text=time_text, text_color=warning_color)
            
            # Play warning sound once per warning level
            warning_key = f"warning_{triggered_warning['percentage']}"
            if not hasattr(self, '_triggered_warnings'):
                self._triggered_warnings = set()
            
            if warning_key not in self._triggered_warnings:
                self._triggered_warnings.add(warning_key)
                # Play the warning sound
                self.play_warning_sound_file(triggered_warning.get('sound', 'assets/bell.wav'))
        else:
            # No warning - use normal timer color
            self.timer_label.configure(text=time_text, text_color=self.theme.get("timer_normal", self.theme.get("timer", self.theme["primary"])))
        
        # Update progress bar
        self.update_progress()
    
    def update_progress(self):
        """Update the session progress bar"""
        if not self.session_controller.session:
            return
        
        # Calculate total session duration
        total_duration = sum(block.duration for block in self.session_controller.session.blocks)
        
        # Calculate time elapsed
        current_block_index = self.session_controller.current_block_index
        elapsed = 0
        
        # Add duration of completed blocks
        for i in range(current_block_index):
            elapsed += self.session_controller.session.blocks[i].duration
        
        # Add elapsed time in current block
        current_block = self.session_controller.session.blocks[current_block_index]
        time_into_current_block = current_block.duration - self.session_controller.remaining
        elapsed += time_into_current_block
        
        # Calculate percentage
        if total_duration > 0:
            progress = elapsed / total_duration
        else:
            progress = 0
        
        # Update progress bar
        self.progress_bar.set(progress)
        
    def handle_session_end(self):
        """Called when session completes"""
        self.block_info_label.configure(text="Session complete!")
        self.folder_tag_label.configure(text="")
        self._update_nsfw_badge(None)
        self.pause_button.configure(text="⏸")
        
        # Hide history and stop buttons, show start button
        self._disable_button(self.history_button)
        self._disable_button(self.stop_button)
        
        # Display completion message on canvas
        self.image_canvas.delete("all")
        canvas_width = self.image_canvas.winfo_width()
        canvas_height = self.image_canvas.winfo_height()
        self.image_canvas.create_text(
            canvas_width // 2,
            canvas_height // 2,
            text="Session Complete!\n\nGreat work!",
            fill="#67E8F9",
            font=("Arial", 24, "bold"),
            justify="center"
        )
        
        # Update progress to 100%
        self.progress_bar.set(1.0)
        
        # Show start button again
        self._show_button(
            self.start_button,
            fg_color=self.theme["success"],
            hover_color=self.theme["success"],
            text_color=self.text_for_success
        )

    def toggle_pause(self):
        """Pause or resume the session"""
        if self.session_controller.state == SessionState.RUNNING:
            self.session_controller.pause()
            self.pause_button.configure(text="▶")
        elif self.session_controller.state == SessionState.PAUSED:
            self.session_controller.resume()
            self.pause_button.configure(text="⏸")

    def stop_session(self):
        """Stop the current session"""
        self.session_controller.stop()
        self.block_info_label.configure(text="Session stopped")
        self.folder_tag_label.configure(text="")
        self._update_nsfw_badge(None)
        self.timer_label.configure(text="00:00")
        self.pause_button.configure(text="⏸")
        
        # Hide history and stop buttons, show start button
        self._disable_button(self.history_button)
        self._disable_button(self.stop_button)
        
        # Reset progress bar
        self.progress_bar.set(0)
        
        # Show start button again
        self._show_button(
            self.start_button,
            fg_color=self.theme["success"],
            hover_color=self.theme["success"],
            text_color=self.text_for_success
        )

    def show_image_history(self):
        """Show dialog with all images from current block"""
        if not self.session_controller.session:
            return
        
        # Get current block index and history
        current_block_idx = self.session_controller.current_block_index
        current_block = self.session_controller.session.blocks[current_block_idx]
        
        # Only show for pose blocks
        if current_block.block_type != "pose":
            return
        
        # Get block start and end indices - show ALL images ever seen in this block
        block_start = self.session_controller.block_start_indices.get(current_block_idx, 0)
        current_idx = self.session_controller.current_image_index
        
        # Show everything from block start to the furthest image reached
        # (not just current - user may have gone back, history should be preserved)
        furthest_idx = max(
            self.session_controller.block_last_indices.get(current_block_idx, current_idx),
            current_idx
        )
        
        block_images = []
        for i in range(block_start, furthest_idx + 1):
            if i < len(self.session_controller.image_history):
                img_path = self.session_controller.image_history[i]
                if img_path:  # Skip None (break images)
                    block_images.append(img_path)
        
        if not block_images:
            return
        
        # Pass current position within the block so dialog can highlight it
        current_pos = current_idx - block_start
        ImageHistoryDialog(self, block_images, current_pos)
    
    def open_settings(self):
        """Open settings dialog with keyboard shortcuts"""
        SettingsDialog(self, self.shortcuts_manager)
    
    def play_warning_sound_file(self, sound_file_path: str):
        """Play a specific warning sound file with volume control"""
        def _play():
            try:
                import json
                import wave
                import struct
                import tempfile
                import winsound
                
                sound_path = Path(resource_path(sound_file_path)) if sound_file_path.startswith("assets/") else Path(sound_file_path)
                
                if not sound_path.exists():
                    return
                
                # Load volume setting
                volume_file = Path("settings/volume.json")
                volume = 0.7  # Default
                
                if volume_file.exists():
                    with open(volume_file, 'r') as f:
                        volumes = json.load(f)
                        volume = volumes.get('warning', 0.7)
                
                # Scale volume (0.0 to 1.0)
                if volume <= 0:
                    return
                
                # Read WAV file
                with wave.open(str(sound_path), 'rb') as wav_file:
                    frames = wav_file.readframes(wav_file.getnframes())
                    params = wav_file.getparams()
                
                # Adjust volume
                samples = struct.unpack(f'{len(frames)//2}h', frames)
                scaled_samples = [int(sample * volume) for sample in samples]
                scaled_frames = struct.pack(f'{len(scaled_samples)}h', *scaled_samples)
                
                # Write to temp file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                    temp_path = temp_wav.name
                    with wave.open(temp_path, 'wb') as temp_wav_file:
                        temp_wav_file.setparams(params)
                        temp_wav_file.writeframes(scaled_frames)
                
                # Play sound
                winsound.PlaySound(temp_path, winsound.SND_FILENAME)
                
                # Clean up
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
            except Exception as e:
                print(f"Error playing warning sound: {e}")
        
        # Play in background thread
        threading.Thread(target=_play, daemon=True).start()

    def play_transition_sound(self):
        """Play transition sound with volume control"""
        def _play():
            try:
                import json
                import wave
                import struct
                import tempfile
                import winsound
                
                # Load sound file path from settings
                sound_file = Path("settings/sounds.json")
                default_path = "assets/Universfield_messageincoming2.wav"
                
                if sound_file.exists():
                    with open(sound_file, 'r') as f:
                        sounds = json.load(f)
                        sound_path_str = sounds.get('transition', default_path)
                else:
                    sound_path_str = default_path
                
                sound_path = Path(resource_path(sound_path_str)) if sound_path_str.startswith("assets/") else Path(sound_path_str)
                
                if not sound_path.exists():
                    return
                
                # Load volume setting
                volume_file = Path("settings/volume.json")
                volume = 1.0  # Default (100%)
                
                if volume_file.exists():
                    with open(volume_file, 'r') as f:
                        volumes = json.load(f)
                        volume = volumes.get('transition', 0.5)
                
                # Read original WAV
                with wave.open(str(sound_path), 'rb') as wf:
                    params = wf.getparams()
                    frames = wf.readframes(params.nframes)
                
                # Adjust volume
                samples = struct.unpack(f'{params.nframes * params.nchannels}h', frames)
                adjusted_samples = [int(sample * volume) for sample in samples]
                adjusted_frames = struct.pack(f'{len(adjusted_samples)}h', *adjusted_samples)
                
                # Write to temporary file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                    temp_path = temp_wav.name
                    with wave.open(temp_path, 'wb') as wf:
                        wf.setparams(params)
                        wf.writeframes(adjusted_frames)
                
                # Play with winsound
                winsound.PlaySound(temp_path, winsound.SND_FILENAME)
                
                # Cleanup
                Path(temp_path).unlink()
                
            except:
                pass  # Silently fail if sound doesn't work
        
        threading.Thread(target=_play, daemon=True).start()
    
    def toggle_always_on_top(self):
        """Toggle window always on top"""
        self.is_pinned = not self.is_pinned
        self.attributes('-topmost', self.is_pinned)
        
        # Update button appearance to show pinned state
        if self.is_pinned:
            # Pinned - highlight the button
            self.pin_button.configure(
                fg_color=self.theme["primary"],
                text_color=self.text_for_primary
            )
        else:
            # Unpinned - normal appearance
            CYBER_GRAY = self.theme["gray"]
            self.pin_button.configure(
                fg_color=CYBER_GRAY,
                text_color=self.theme["text"]
            )
    
    def show_image_context_menu(self, event):
        """Show right-click menu for image tagging"""
        if not self.current_image_path:
            return
        
        import tkinter as tk
        menu = tk.Menu(self, tearoff=0)
        
        # Check current NSFW status
        filename = os.path.basename(str(self.current_image_path))
        is_nsfw = '_nsfw' in filename.lower()
        
        if is_nsfw:
            menu.add_command(
                label="✓ Tagged as NSFW",
                state="disabled"
            )
            menu.add_command(
                label="Remove NSFW tag",
                command=self.tag_image_sfw
            )
        else:
            menu.add_command(
                label="✓ Tagged as SFW",
                state="disabled"
            )
            menu.add_command(
                label="Tag as NSFW",
                command=self.tag_image_nsfw
            )
        
        menu.post(event.x_root, event.y_root)
    
    def tag_image_nsfw(self):
        """Rename file to add _nsfw tag"""
        if not self.current_image_path:
            return
        
        filepath = Path(self.current_image_path)
        filename = filepath.stem
        extension = filepath.suffix
        
        # Don't add if already tagged (case-insensitive check)
        if '_nsfw' in filename.lower():
            return
        
        # New filename with _nsfw (lowercase to match filter logic)
        new_filename = f"{filename}_nsfw{extension}"
        new_filepath = filepath.parent / new_filename
        
        try:
            # Remove old path from cache before renaming
            if filepath in self._image_cache:
                del self._image_cache[filepath]
            
            # Get current block's filter
            current_block = self.session_controller.session.blocks[
                self.session_controller.current_block_index
            ]
            current_filter = current_block.nsfw_filter
            
            if hasattr(self.session_controller, 'used_images_in_session'):
                if filepath in self.session_controller.used_images_in_session:
                    self.session_controller.used_images_in_session.remove(filepath)

            filepath.rename(new_filepath)
            
            # Update image collection cache
            self.image_collection.refresh_file(filepath, new_filepath)
            
            # Add new path to used set; flag auto-advance if no longer valid for filter
            should_auto_advance = False
            if hasattr(self.session_controller, 'used_images_in_session'):
                self.session_controller.used_images_in_session.add(new_filepath)
                if current_filter not in ("all", "nsfw"):
                    should_auto_advance = True
            
            # Update current path
            self.current_image_path = new_filepath
            # print(f"Tagged as NSFW: {new_filename}")
            
            # Update ALL occurrences in image history (not just current)
            if hasattr(self.session_controller, 'image_history'):
                for i in range(len(self.session_controller.image_history)):
                    if self.session_controller.image_history[i] == filepath:
                        self.session_controller.image_history[i] = new_filepath
            
            # If image no longer matches filter, auto-advance to next valid image
            if should_auto_advance:
                self.next_image()  # Automatically go to next image
            else:
                # Refresh display immediately with new filename
                self.display_image(new_filepath)
                self._update_nsfw_badge(new_filepath)
            
        except Exception as e:
            print(f"Error tagging image: {e}")
            import traceback
            traceback.print_exc()
    
    def tag_image_sfw(self):
        """Rename file to remove _nsfw tag"""
        if not self.current_image_path:
            return
        
        filepath = Path(self.current_image_path)
        filename = filepath.stem
        extension = filepath.suffix
        
        # Remove _nsfw from filename (case-insensitive)
        import re
        new_filename_stem = re.sub(r'_nsfw', '', filename, flags=re.IGNORECASE)
        new_filename = f"{new_filename_stem}{extension}"
        new_filepath = filepath.parent / new_filename
        
        try:
            # Remove old path from cache before renaming
            if filepath in self._image_cache:
                del self._image_cache[filepath]
            
            # Get current block's filter
            current_block = self.session_controller.session.blocks[
                self.session_controller.current_block_index
            ]
            current_filter = current_block.nsfw_filter
            
            if hasattr(self.session_controller, 'used_images_in_session'):
                if filepath in self.session_controller.used_images_in_session:
                    self.session_controller.used_images_in_session.remove(filepath)

            filepath.rename(new_filepath)
            
            # Update image collection cache
            self.image_collection.refresh_file(filepath, new_filepath)
            
            # Add new path to used set; flag auto-advance if no longer valid for filter
            should_auto_advance = False
            if hasattr(self.session_controller, 'used_images_in_session'):
                self.session_controller.used_images_in_session.add(new_filepath)
                if current_filter not in ("all", "sfw"):
                    should_auto_advance = True
            
            # Update current path
            self.current_image_path = new_filepath
            # print(f"Tagged as SFW: {new_filename}")
            
            # Update ALL occurrences in image history (not just current)
            if hasattr(self.session_controller, 'image_history'):
                for i in range(len(self.session_controller.image_history)):
                    if self.session_controller.image_history[i] == filepath:
                        self.session_controller.image_history[i] = new_filepath
            
            # If image no longer matches filter, auto-advance to next valid image
            if should_auto_advance:
                self.next_image()  # Automatically go to next image
            else:
                # Refresh display immediately with new filename
                self.display_image(new_filepath)
                self._update_nsfw_badge(new_filepath)
            
        except Exception as e:
            print(f"Error tagging image: {e}")
            import traceback
            traceback.print_exc()
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        
        if self.is_fullscreen:
            self.attributes("-fullscreen", True)
            self.state('zoomed')  # Windows
        else:
            self.attributes("-fullscreen", False)
            self.state('normal')
        
        self.update_idletasks()
    
    def exit_fullscreen(self, event=None):
        """Exit fullscreen mode (called by ESC key)"""
        if self.is_fullscreen:
            self.toggle_fullscreen()

    def display_image(self, image_path: Path):
        """Display an image on canvas, scaled to fit available space"""
        # Store current image path for right-click tagging
        self.current_image_path = image_path
        
        # Force UI update FIRST so buttons appear immediately
        self.update_idletasks()
        
        # Get canvas dimensions
        canvas_width = self.image_canvas.winfo_width()
        canvas_height = self.image_canvas.winfo_height()
        
        # Load PIL image from cache
        if image_path not in self._image_cache:
            self._image_cache[image_path] = Image.open(image_path)
        
        img = self._image_cache[image_path]
        
        # Calculate scaled size maintaining aspect ratio
        img_ratio = img.width / img.height
        canvas_ratio = canvas_width / canvas_height

        if img_ratio > canvas_ratio:
            # Width-constrained
            new_width = canvas_width
            new_height = int(canvas_width / img_ratio)
        else:
            # Height-constrained
            new_height = canvas_height
            new_width = int(canvas_height * img_ratio)

        resized_img = img.resize((new_width, new_height), Image.Resampling.BILINEAR)
        
        # Convert to PhotoImage for tkinter Canvas
        self.canvas_image_ref = ImageTk.PhotoImage(resized_img)
        
        self.image_canvas.delete("all")
        x = canvas_width // 2
        y = canvas_height // 2
        self.image_canvas.create_image(
            x, y, image=self.canvas_image_ref, anchor="center"
        )
        
        # Store for resize handler
        self.current_displayed_image = image_path

    def display_break(self):
        """Display break screen on canvas"""
        # Force UI update first
        self.update_idletasks()
        
        # Get canvas dimensions
        canvas_width = self.image_canvas.winfo_width()
        canvas_height = self.image_canvas.winfo_height()

        # Calculate scaled size for break image
        img_ratio = self.break_image.width / self.break_image.height
        canvas_ratio = canvas_width / canvas_height

        if img_ratio > canvas_ratio:
            new_width = canvas_width
            new_height = int(canvas_width / img_ratio)
        else:
            new_height = canvas_height
            new_width = int(canvas_height * img_ratio)

        # Resize image with fast algorithm
        resized_img = self.break_image.resize((new_width, new_height), Image.Resampling.BILINEAR)
        
        # Convert to PhotoImage
        self.canvas_image_ref = ImageTk.PhotoImage(resized_img)
        
        # Clear canvas and draw image centered
        self.image_canvas.delete("all")
        x = canvas_width // 2
        y = canvas_height // 2
        self.image_canvas.create_image(
            x, y, image=self.canvas_image_ref, anchor="center"
        )
        
        self.current_displayed_image = None

    def start_session(self, session: Session):
        """Start any session (called by session selector or test button)"""
        # Hide start button, show stop button
        self._disable_button(self.start_button)
        self._show_button(
            self.stop_button,
            fg_color=self.theme["primary"],
            hover_color=self.theme["primary"],
            text_color=self.text_for_primary
        )
        
        # Show history button
        self._show_button(
            self.history_button,
            fg_color=self.theme["accent"],
            hover_color=self.theme["primary"],
            text_color=self.text_for_accent
        )
        
        # Force UI update so buttons update right away
        self.update_idletasks()
        
        # Now do the heavy work
        self.session_controller.start(session)
    
    def open_session_builder(self):
        """Open the session builder dialog"""
        dialog = SessionBuilderDialog(self)
        self.wait_window(dialog)
        
        # Check if user created a session
        session = dialog.get_result()
        if session:
            self.start_session(session)
    
    def start_test_session(self):
        """Start a test session for development - 1 Hr Class Mode"""
        blocks = []
        
        # 10 poses, 30 seconds each
        for _ in range(10):
            blocks.append(SessionBlock(block_type="pose", duration=30, count=1, folder_paths=None))
        
        # 5 poses, 1 minute each
        for _ in range(5):
            blocks.append(SessionBlock(block_type="pose", duration=60, count=1, folder_paths=None))
        
        # 2 poses, 5 minutes each
        for _ in range(2):
            blocks.append(SessionBlock(block_type="pose", duration=300, count=1, folder_paths=None))
        
        # 1 pose, 10 minutes
        blocks.append(SessionBlock(block_type="pose", duration=600, count=1, folder_paths=None))
        
        # Break, 5 minutes
        blocks.append(SessionBlock(block_type="break", duration=300, count=1))
        
        # 1 pose, 25 minutes
        blocks.append(SessionBlock(block_type="pose", duration=1500, count=1, folder_paths=None))
        
        test_session = Session(name="1 Hr Class Mode", blocks=blocks)
        self.start_session(test_session)
    
    def run(self):
        self.mainloop()


class ImageHistoryDialog(ctk.CTkToplevel):
    """Dialog showing all images from current block"""
    
    def __init__(self, parent, images: list, current_index: int):
        super().__init__(parent)
        
        self.parent_window = parent
        self.images = images
        self.current_index = current_index
        
        # Dialog setup
        self.title("Image History - Current Block")
        self.geometry("900x700")
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Load theme colors
        from theme_config import get_theme, load_current_theme, get_text_color_for_bg
        theme = get_theme(load_current_theme())
        
        # Colors
        CYBER_DARK = theme["dark"]
        CYBER_GRAY = theme["gray"]
        CYBER_BLUE = theme["secondary"]
        CYBER_PINK = theme["primary"]
        CYBER_TEXT = theme["text"]
        
        TEXT_FOR_BLUE = get_text_color_for_bg(CYBER_BLUE)
        
        # Store theme for hover effects
        self.theme = theme
        
        self.configure(fg_color=CYBER_DARK)
        
        # Main frame
        main_frame = ctk.CTkFrame(self, fg_color=CYBER_DARK)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkLabel(
            main_frame,
            text=f"📜 Image History ({len(images)} images in this block)",
            font=("Arial", 18, "bold"),
            text_color=CYBER_BLUE
        )
        header.pack(pady=(0, 15))
        
        # Scrollable frame for images
        scroll_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color=CYBER_GRAY
        )
        scroll_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Display images in a grid (3 columns)
        for idx, img_path in enumerate(images):
            try:
                # Create frame for each image (make it clickable)
                img_frame = ctk.CTkFrame(scroll_frame, fg_color=CYBER_GRAY, corner_radius=8)
                img_frame.grid(row=idx//3, column=idx%3, padx=10, pady=10, sticky="nsew")
                
                # Make frame clickable
                img_frame.bind("<Button-1>", lambda e, index=idx: self.jump_to_image(index))
                img_frame.bind("<Enter>", lambda e, frame=img_frame: frame.configure(fg_color=self.theme["light_gray"]))
                img_frame.bind("<Leave>", lambda e, frame=img_frame: frame.configure(fg_color=CYBER_GRAY))
                
                # Load and resize image
                pil_image = Image.open(img_path)
                pil_image.thumbnail((250, 250), Image.Resampling.LANCZOS)
                
                ctk_image = ctk.CTkImage(
                    light_image=pil_image,
                    dark_image=pil_image,
                    size=pil_image.size
                )
                
                # Image label
                img_label = ctk.CTkLabel(
                    img_frame,
                    image=ctk_image,
                    text="",
                    cursor="hand2"
                )
                img_label.pack(padx=5, pady=5)
                
                # Make image label also clickable
                img_label.bind("<Button-1>", lambda e, index=idx: self.jump_to_image(index))
                
                # Image number and indicator
                is_current = (idx == current_index)
                number_text = f"#{idx + 1}" + (" ← Current" if is_current else "")
                number_color = CYBER_PINK if is_current else CYBER_TEXT
                
                number_label = ctk.CTkLabel(
                    img_frame,
                    text=number_text,
                    font=("Arial", 11, "bold" if is_current else "normal"),
                    text_color=number_color,
                    cursor="hand2"
                )
                number_label.pack(pady=(0, 5))
                
                # Make number label clickable too
                number_label.bind("<Button-1>", lambda e, index=idx: self.jump_to_image(index))
                
            except Exception as e:
                # If image fails to load, show placeholder
                error_label = ctk.CTkLabel(
                    scroll_frame,
                    text=f"❌ Failed to load\n{img_path.name}",
                    font=("Arial", 10),
                    text_color="#FF3333"
                )
                error_label.grid(row=idx//3, column=idx%3, padx=10, pady=10)
        
        # Configure grid columns to be equal width
        for col in range(3):
            scroll_frame.grid_columnconfigure(col, weight=1, uniform="images")
        
        # Close button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Close",
            command=self.destroy,
            font=("Arial", 13, "bold"),
            fg_color=CYBER_BLUE,
            hover_color=CYBER_PINK,
            text_color=TEXT_FOR_BLUE,  # Smart text color
            width=120,
            height=35
        )
        close_btn.pack()
    
    def jump_to_image(self, index: int):
        """Jump to selected image in history"""
        # Get the absolute index in image history
        block_start = self.parent_window.session_controller.block_start_indices.get(
            self.parent_window.session_controller.current_block_index, 0
        )
        absolute_index = block_start + index
        
        # Set the controller to this image
        self.parent_window.session_controller.current_image_index = absolute_index
        
        # Only update block_last_indices if jumping FORWARD (never shrink the furthest-reached tracker)
        current_last = self.parent_window.session_controller.block_last_indices.get(
            self.parent_window.session_controller.current_block_index, 0
        )
        if absolute_index > current_last:
            self.parent_window.session_controller.block_last_indices[
                self.parent_window.session_controller.current_block_index
            ] = absolute_index
        
        # Get current block and image
        block = self.parent_window.session_controller.session.blocks[
            self.parent_window.session_controller.current_block_index
        ]
        image_path = self.parent_window.session_controller.image_history[absolute_index]
        
        # Increment version to reset timer with new thread
        self.parent_window.session_controller._transitioning = True
        self.parent_window.session_controller._transition_version += 1
        current_version = self.parent_window.session_controller._transition_version
        
        # Reset timer
        self.parent_window.session_controller.remaining = block.duration
        self.parent_window.session_controller.block_start_time = __import__('time').time()
        
        self.parent_window.session_controller._transitioning = False
        
        # Notify GUI to display the image
        if self.parent_window.session_controller.on_new_block:
            self.parent_window.session_controller.on_new_block(
                self.parent_window.session_controller.current_block_index,
                block,
                image_path
            )
        
        # Stop old timer and start new one with new version
        if self.parent_window.session_controller._timer_thread:
            self.parent_window.session_controller._stop_flag.set()
            self.parent_window.session_controller._stop_flag.clear()
        
        self.parent_window.session_controller._timer_thread = threading.Thread(
            target=self.parent_window.session_controller._timer_loop,
            args=(current_version,),
            daemon=True
        )
        self.parent_window.session_controller._timer_thread.start()
        
        # Close dialog
        self.destroy()
if __name__ == "__main__":
    app = MainWindow()
    app.run()