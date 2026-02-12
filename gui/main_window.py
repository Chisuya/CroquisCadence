import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import customtkinter as ctk
from pathlib import Path
from PIL import Image, ImageTk
from typing import Optional

from models.session import Session, SessionBlock
from models.image_collection import ImageCollection
from controllers.session_controller import SessionController, SessionState
from controllers.keyboard_shortcuts import KeyboardShortcutsManager
from gui.session_builder import SessionBuilderDialog
from gui.settings_dialog import SettingsDialog


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("CroquisCadence")
        self.geometry("1400x800")
        self.resizable(True, True)
        self.configure(fg_color="#0f0f0f")

        ctk.set_appearance_mode("dark")
        
        # Initialize controllers
        self.image_collection = ImageCollection(Path("test_data/references"))
        self.session_controller = SessionController(self.image_collection)
        self.shortcuts_manager = KeyboardShortcutsManager()
        
        # Register session callbacks
        self.session_controller.on_new_block = self.handle_new_block
        self.session_controller.on_tick = self.handle_tick
        self.session_controller.on_session_end = self.handle_session_end
        
        # Register keyboard shortcut callbacks
        self.setup_keyboard_shortcuts()
        
        # State
        self.current_image_path: Optional[Path] = None
        self.is_fullscreen = False
        
        # Image caching
        self._image_cache = {}  # Caches PIL Image objects
        self._scaled_cache = {}  # Caches scaled CTkImage objects (key: (path, width, height))
        
        self.create_widgets()
        
        self.break_image = Image.open("assets/break_image.png")

        # Bind window resize to update image
        self.bind("<Configure>", self.on_window_resize)
        
        # Bind ESC key to exit fullscreen
        self.bind("<Escape>", self.exit_fullscreen)
        
        # Bind keyboard shortcuts
        self.bind_keyboard_shortcuts()

        # Store current image path for resizing
        self.current_displayed_image: Optional[Path] = None
    
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

    def _get_available_image_space(self):
        """
        Get available space from the image frame.
        Returns dimensions that will DEFINITELY fit within the visible area.
        """
        # Force complete layout update
        self.update_idletasks()
        
        # Get frame dimensions
        frame_height = self.image_frame.winfo_height()
        frame_width = self.image_frame.winfo_width()
        
        # If not yet laid out, force update
        if frame_width <= 1 or frame_height <= 1:
            self.update()
            frame_width = self.image_frame.winfo_width()
            frame_height = self.image_frame.winfo_height()
        
        # Use frame dimensions directly with tiny margin
        available_height = max(100, frame_height - 10)
        available_width = max(100, frame_width - 10)
        
        return available_width, available_height

    def on_window_resize(self, event):
        """Handle window resize - rescale current image"""
        # Only resize if an image is displayed
        if self.current_displayed_image and self.session_controller.state != SessionState.IDLE:
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
        # Fixes NoneType object has no attribute "blocks" error
        if not self.session_controller.session:
            return
        
        """Show next image for current block, skip breaks"""
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
        CYBER_PINK = "#FF6EC7"
        CYBER_DPINK = "#D74AB2"
        CYBER_PURPLE = "#B794F6"
        CYBER_VIOLET = "#8B5CF6"
        CYBER_BLUE = "#67E8F9"
        CYBER_DBLUE = "#579DDE"
        CYBER_GREEN = "#67F971"
        CYBER_TEAL = "#1CBC7C"
        CYBER_ACCENT = "#A78BFA"
        CYBER_DARK = "#0f0f0f"
        CYBER_GRAY = "#1f1f1f"
        CYBER_TEXT = "#E5E5E5"
        
        self.main_container = ctk.CTkFrame(self, fg_color=CYBER_DARK)
        self.main_container.pack(fill="both", expand=True, padx=0, pady=0)

        # Thin progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.main_container,
            height=4,
            corner_radius=0,
            progress_color=CYBER_BLUE,
            fg_color="#1a1a1a"
        )
        self.progress_bar.pack(fill="x", side="bottom", padx=0, pady=(0, 0))
        self.progress_bar.set(0)

        # Controls bar
        self.info_bar = ctk.CTkFrame(self.main_container, fg_color=CYBER_GRAY, height=100)
        self.info_bar.pack(fill="x", side="bottom", padx=20, pady=20)
        self.info_bar.pack_propagate(False)  # Keep fixed height
        
        self.info_bar.grid_columnconfigure(0, weight=1)  # left
        self.info_bar.grid_columnconfigure(1, weight=1)  # center
        self.info_bar.grid_columnconfigure(2, weight=1)  # right

        # Block info
        self.block_info_label = ctk.CTkLabel(
            self.info_bar,
            text="Ready to start",
            font=("Arial", 16),
            text_color=CYBER_BLUE,
            anchor="w",
            width=300
        )
        self.block_info_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Timer
        self.timer_label = ctk.CTkLabel(
            self.info_bar,
            text="00:00",
            font=("Arial", 32, "bold"),
            text_color=CYBER_PINK
        )
        self.timer_label.grid(row=0, column=2, padx=20, pady=10, sticky="e")

        # Control buttons
        self.button_frame = ctk.CTkFrame(self.info_bar, fg_color=CYBER_GRAY)
        self.button_frame.grid(row=0, column=1, padx=5, pady=10)

        # Start button
        self.start_button = ctk.CTkButton(
            self.button_frame,
            text="▶ START",
            command=self.open_session_builder,
            width=100,
            fg_color=CYBER_GREEN,
            hover_color=CYBER_TEAL,
            text_color="white",
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
            hover_color=CYBER_VIOLET,
            text_color="white",
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
            hover_color=CYBER_DBLUE,
            text_color="black",
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
            hover_color=CYBER_DPINK,
            text_color="white",
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
            hover_color=CYBER_DBLUE,
            text_color="black",
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
            hover_color=CYBER_VIOLET,
            text_color="white",
            font=("Arial", 20)
        )
        self.next_block_button.pack(side="left", padx=5)

        # Stop button
        self.stop_button = ctk.CTkButton(
            self.button_frame,
            text="⏹ STOP",
            command=self.stop_session,
            width=100,
            fg_color=CYBER_PINK,
            hover_color=CYBER_DPINK,
            text_color="white",
            font=("Arial", 13, "bold")
        )
        self.stop_button.pack(side="left", padx=5)

        # Settings button
        self.settings_button = ctk.CTkButton(
            self.button_frame,
            text="⚙",
            command=self.open_settings,
            width=60,
            fg_color="#2D3748",
            hover_color=CYBER_ACCENT,
            border_width=2,
            border_color=CYBER_BLUE,
            text_color=CYBER_TEXT,
            font=("Arial", 18)
        )
        self.settings_button.pack(side="left", padx=5)

        # Fullscreen button
        self.fullscreen_button = ctk.CTkButton(
            self.button_frame,
            text="⛶",
            command=self.toggle_fullscreen,
            width=60,
            fg_color="#2D3748",
            hover_color=CYBER_ACCENT,
            border_width=2,
            border_color=CYBER_BLUE,
            text_color=CYBER_TEXT,
            font=("Arial", 18)
        )
        self.fullscreen_button.pack(side="left", padx=5)

        # Image display area
        self.image_frame = ctk.CTkFrame(self.main_container, fg_color=CYBER_DARK)
        self.image_frame.pack(fill="both", expand=True, padx=5, pady=(5, 0))

        # Use Canvas instead of Label to prevent overflow and cropping issues
        import tkinter as tk
        self.image_canvas = tk.Canvas(
            self.image_frame,
            bg="#0f0f0f",
            highlightthickness=0,
            bd=0
        )
        self.image_canvas.pack(fill="both", expand=True)
        
        # Store canvas image reference
        self.canvas_image_id = None
        self.canvas_image_ref = None
    
    def handle_new_block(self, block_index, block, image_path):
        """Called when a new block starts"""
        total_blocks = len(self.session_controller.session.blocks)
        
        current_duration = block.duration
        remaining_same_duration = 0
        
        # Count from current block onwards
        for i in range(block_index, total_blocks):
            check_block = self.session_controller.session.blocks[i]
            if check_block.block_type == block.block_type and check_block.duration == current_duration:
                remaining_same_duration += 1
        
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
                block_text = f"{remaining_same_duration} more of this length, {duration_str} each"
            else:
                block_text = f"Last {duration_str} pose"
        else:
            minutes = current_duration // 60
            block_text = f"Break - {minutes}m"
        
        self.block_info_label.configure(text=block_text)

        # Update progress bar
        self.update_progress()

        if block.block_type == "pose" and image_path:
            self.display_image(image_path)
        else:
            self.display_break()
        
    def handle_tick(self, remaining):
        """Called every second during countdown"""
        # Update timer display
        minutes = remaining // 60
        seconds = remaining % 60
        time_text = f"{minutes:02d}:{seconds:02d}"
        self.timer_label.configure(text=time_text)
        
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
        self.pause_button.configure(text="⏸")
        
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
        self.start_button.pack(side="left", padx=5, before=self.prev_block_button)

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
        self.timer_label.configure(text="00:00")
        self.pause_button.configure(text="⏸")
        
        # Reset progress bar
        self.progress_bar.set(0)
        
        # Show start button again
        self.start_button.pack(side="left", padx=5, before=self.prev_block_button)

    def open_settings(self):
        """Open settings dialog with keyboard shortcuts"""
        SettingsDialog(self, self.shortcuts_manager)

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        
        if self.is_fullscreen:
            self.attributes("-fullscreen", True)
            self.state('zoomed')  # Windows
            self.fullscreen_button.configure(text="⛶ Exit")
        else:
            self.attributes("-fullscreen", False)
            self.state('normal')
            self.fullscreen_button.configure(text="⛶ Full")
        
        self.update_idletasks()
    
    def exit_fullscreen(self, event=None):
        """Exit fullscreen mode (called by ESC key)"""
        if self.is_fullscreen:
            self.toggle_fullscreen()

    def display_image(self, image_path: Path):
        """Display an image on canvas, scaled to fit available space"""
        # Get canvas dimensions
        self.update_idletasks()
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

        # Resize image
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage for tkinter Canvas
        self.canvas_image_ref = ImageTk.PhotoImage(resized_img)
        
        # Clear canvas and draw image centered
        self.image_canvas.delete("all")
        x = canvas_width // 2
        y = canvas_height // 2
        self.canvas_image_id = self.image_canvas.create_image(
            x, y, image=self.canvas_image_ref, anchor="center"
        )
        
        # Store for resize handler
        self.current_displayed_image = image_path

    def display_break(self):
        """Display break screen on canvas"""
        # Get canvas dimensions
        self.update_idletasks()
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

        # Resize image
        resized_img = self.break_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        self.canvas_image_ref = ImageTk.PhotoImage(resized_img)
        
        # Clear canvas and draw image centered
        self.image_canvas.delete("all")
        x = canvas_width // 2
        y = canvas_height // 2
        self.canvas_image_id = self.image_canvas.create_image(
            x, y, image=self.canvas_image_ref, anchor="center"
        )
        
        self.current_displayed_image = None

    def start_session(self, session: Session):
        """Start any session (called by session selector or test button)"""
        self.session_controller.start(session)
        
        self.start_button.pack_forget()
    
    def open_session_builder(self):
        """Open the session builder dialog"""
        dialog = SessionBuilderDialog(self)
        self.wait_window(dialog)  # Wait for dialog to close
        
        # Check if user created a session
        session = dialog.get_result()
        if session:
            self.start_session(session)
    
    def on_session_selected(self, selected_session):
        """Called when user picks a session from menu/dialog"""
        self.start_session(selected_session)

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


if __name__ == "__main__":
    app = MainWindow()
    app.run()