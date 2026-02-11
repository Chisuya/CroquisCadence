import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import customtkinter as ctk
from pathlib import Path
from PIL import Image
from typing import Optional

from models.session import Session, SessionBlock
from models.image_collection import ImageCollection
from controllers.session_controller import SessionController, SessionState
from gui.session_builder import SessionBuilderDialog


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
        
        # Register callbacks
        self.session_controller.on_new_block = self.handle_new_block
        self.session_controller.on_tick = self.handle_tick
        self.session_controller.on_session_end = self.handle_session_end
        
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

        # Store current image path for resizing
        self.current_displayed_image: Optional[Path] = None

    def _get_available_image_space(self):
        """
        Get available space from the image frame.
        Frame size is now reliable because image label uses place() geometry.
        """
        # Force layout update
        self.update_idletasks()
        
        frame_width = self.image_frame.winfo_width()
        frame_height = self.image_frame.winfo_height()
        
        # If not laid out yet, force update and retry
        if frame_width <= 1 or frame_height <= 1:
            self.update()
            frame_width = self.image_frame.winfo_width()
            frame_height = self.image_frame.winfo_height()
        
        available_width = max(100, frame_width - 40)
        available_height = max(100, frame_height - 40)
        
        return available_width, available_height

    def on_window_resize(self, event):
        """Handle window resize - rescale current image"""
        # Only resize if we have an image displayed
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

        # Info/controls bar
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
            anchor="w",  # Align text to left within its cell
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
        self.image_frame.pack(fill="both", expand=True, padx=20, pady=(20, 0))

        # Image label
        # !!use place() instead of pack() to prevent overflow
        self.image_label = ctk.CTkLabel(
            self.image_frame,
            text="",
            fg_color=CYBER_DARK
        )
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")
    
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

        if block.block_type == "pose" and image_path:
            self.display_image(image_path)
        else:
            self.display_break()
        
    def handle_tick(self, remaining):
        """Called every second during countdown"""
        # MM:SS
        minutes = remaining // 60
        seconds = remaining % 60
        time_text = f"{minutes:02d}:{seconds:02d}"
        self.timer_label.configure(text=time_text)
        
    def handle_session_end(self):
        """Called when session completes"""
        self.block_info_label.configure(text="Session complete!")
        self.pause_button.configure(text="⏸")
        self.image_label.configure(image="", text="Session Complete!\n\nGreat work!")
        
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
        
        # Show start button again
        self.start_button.pack(side="left", padx=5, before=self.prev_block_button)

    def open_settings(self):
        """Open settings dialog"""
        print("Settings clicked - TODO: implement")

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
        """Display an image, scaled to fit available space"""
        available_width, available_height = self._get_available_image_space()
        
        # Load PIL image from cache
        if image_path not in self._image_cache:
            self._image_cache[image_path] = Image.open(image_path)
        
        img = self._image_cache[image_path]
        
        # Calculate scaled size maintaining aspect ratio
        img_ratio = img.width / img.height
        frame_ratio = available_width / available_height

        if img_ratio > frame_ratio:
            new_width = available_width
            new_height = int(available_width / img_ratio)
        else:
            new_height = available_height
            new_width = int(available_height * img_ratio)

        cache_key = (image_path, new_width, new_height)
        
        if cache_key in self._scaled_cache:
            # Use cached scaled image
            ctk_image = self._scaled_cache[cache_key]
        else:
            # Create new scaled image and cache it
            ctk_image = ctk.CTkImage(
                light_image=img,
                dark_image=img,
                size=(new_width, new_height)
            )
            self._scaled_cache[cache_key] = ctk_image

        self.image_label.configure(image=ctk_image, text="")
        self.image_label.image = ctk_image
        
        # Store for resize handler
        self.current_displayed_image = image_path

    def display_break(self):
        """Display break screen"""
        available_width, available_height = self._get_available_image_space()

        # changed break screen to scale dynamically instead of forced square
        img_ratio = self.break_image.width / self.break_image.height
        frame_ratio = available_width / available_height

        if img_ratio > frame_ratio:
            new_width = available_width
            new_height = int(available_width / img_ratio)
        else:
            new_height = available_height
            new_width = int(available_height * img_ratio)

        ctk_image = ctk.CTkImage(
            light_image=self.break_image,
            dark_image=self.break_image,
            size=(new_width, new_height)
        )

        self.image_label.configure(image=ctk_image, text="")
        self.image_label.image = ctk_image
        
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