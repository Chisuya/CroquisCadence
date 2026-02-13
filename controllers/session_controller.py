from enum import Enum
from typing import Optional, Callable
from pathlib import Path
import threading
import time

from models.session import Session, SessionBlock
from models.image_collection import ImageCollection


class SessionState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


class SessionController:
    def __init__(self, image_collection: ImageCollection):
        """Initialize session controller"""
        self.image_collection = image_collection
        
        # Callbacks
        self.on_new_block: Optional[Callable] = None
        self.on_tick: Optional[Callable] = None
        self.on_session_end: Optional[Callable] = None
        self.on_image_change: Optional[Callable] = None
        
        # State
        self.state = SessionState.IDLE
        self.session: Optional[Session] = None
        self.current_block_index: int = 0
        
        self.is_auto_advance = False
        
        self.image_history: list[Optional[Path]] = []
        self.current_image_index: int = 0
        
        # Timer state
        self.remaining: int = 0
        self.block_start_time: float = 0
        
        # Threading
        self._timer_thread: Optional[threading.Thread] = None
        self._stop_flag = threading.Event()
        self._pause_flag = threading.Event()
        self._current_thread_id = 0  # Unique ID for each timer thread
        
        # Block tracking
        self.block_start_indices: dict[int, int] = {}
        self.block_last_indices: dict[int, int] = {}
        
        # Image repetition prevention
        self.used_images_in_session: set[Path] = set()
        
    def start(self, session: Session):
        """Start a session"""
        if self.state != SessionState.IDLE:
            raise ValueError(f"Cannot start: session is {self.state.value}")
        
        self.session = session
        self.current_block_index = 0
        self.current_image_index = 0
        self.image_history = []
        self.block_start_indices = {}
        self.block_last_indices = {}
        self.used_images_in_session = set()
        self.state = SessionState.RUNNING
        
        # Clear flags
        self._stop_flag.clear()
        self._pause_flag.clear()
        
        self._start_block(0)
    
    def _start_block(self, block_index: int):
        """Start a specific block"""
        if block_index >= len(self.session.blocks):
            self.state = SessionState.COMPLETED
            if self.on_session_end:
                self.on_session_end()
            return
        
        # Capture auto-advance flag before resetting
        is_auto = self.is_auto_advance
        self.is_auto_advance = False
        
        self.current_block_index = block_index
        self.block_start_indices[block_index] = len(self.image_history)
        
        block = self.session.blocks[block_index]
        
        # Set current_image_index to the end of history BEFORE getting image
        self.current_image_index = len(self.image_history)
        
        image_path = self._get_current_image()

        self.block_last_indices[block_index] = self.current_image_index
        
        # Notify GUI - pass is_auto flag if callback supports it
        if self.on_new_block:
            # Try passing is_auto parameter, fallback to old signature
            try:
                self.on_new_block(self.current_block_index, block, image_path, is_auto)
            except TypeError:
                # Callback doesn't accept is_auto parameter
                self.on_new_block(self.current_block_index, block, image_path)
        
        # Start timer for this block
        block_duration = block.duration
        self.remaining = block_duration
        self.block_start_time = time.time()
        
        # Increment thread ID and start new timer
        self._current_thread_id += 1
        thread_id = self._current_thread_id
        
        # Start new timer thread with its ID and duration
        self._timer_thread = threading.Thread(
            target=self._timer_loop,
            args=(thread_id, block_duration),
            daemon=True
        )
        self._timer_thread.start()
    
    def _timer_loop(self, thread_id, duration):
        """Simple timer that just counts down - exits if no longer current thread"""
        remaining = duration  # Local variable to avoid conflicts with other threads
        
        while remaining > 0:
            # Check if this thread has been invalidated
            if thread_id != self._current_thread_id:
                return  # This thread is obsolete, exit immediately
            
            if self._stop_flag.is_set():
                return
            
            if self._pause_flag.is_set():
                time.sleep(0.1)
                continue
            
            # Update shared remaining for display
            self.remaining = remaining
            
            if self.on_tick:
                self.on_tick(remaining)
            
            time.sleep(1)
            remaining -= 1
        
        # Only advance block if this is still the current thread
        if thread_id == self._current_thread_id and not self._stop_flag.is_set():
            self.remaining = 0
            self.is_auto_advance = True  # Mark as automatic advancement
            self._start_block(self.current_block_index + 1)
    
    def _get_current_image(self):
        """Get image at current index, generating if needed"""
        if self.current_image_index < len(self.image_history):
            return self.image_history[self.current_image_index]
        
        # Need to generate new image
        block = self.session.blocks[self.current_block_index]
        
        if block.block_type == "pose":
            # Try to get an image that hasn't been used yet
            max_attempts = 100
            new_image = None
            
            for attempt in range(max_attempts):
                # Get a random image from the folders
                candidate = self.image_collection.get_random_image(
                    folder_names=block.folder_paths,
                    exclude=None  # We'll handle exclusion ourselves
                )
                
                # If this image hasn't been used, use it
                if candidate not in self.used_images_in_session:
                    new_image = candidate
                    break
                
                # If all images have been used, reset and use any image
                if attempt == max_attempts - 1:
                    self.used_images_in_session.clear()
                    new_image = candidate
                    break
            
            # Mark this image as used
            if new_image:
                self.used_images_in_session.add(new_image)
            
            self.image_history.append(new_image)
            return new_image
        else:
            # Break block
            if not self.image_history or self.image_history[-1] is not None:
                self.image_history.append(None)
            return None
    
    def pause(self):
        """Pause session"""
        if self.state == SessionState.RUNNING:
            self._pause_flag.set()
            self.state = SessionState.PAUSED
    
    def resume(self):
        """Resume session"""
        if self.state == SessionState.PAUSED:
            self._pause_flag.clear()
            self.state = SessionState.RUNNING
    
    def stop(self):
        """Stop and reset"""
        self._stop_flag.set()
        if self._timer_thread:
            self._timer_thread.join(timeout=1.0)
        
        self.state = SessionState.IDLE
        self.session = None
        self.current_block_index = 0
        self.current_image_index = 0
        self.image_history = []
        self.block_start_indices = {}
        self.block_last_indices = {}
        self.used_images_in_session = set()  # Clear used images
        self.remaining = 0
    
    def next_image(self):
        """Show next image in global history and reset timer"""
        if self.state not in [SessionState.RUNNING, SessionState.PAUSED]:
            return
        
        block = self.session.blocks[self.current_block_index]
        if block.block_type != "pose":
            return
        
        self.current_image_index += 1
        
        self.block_last_indices[self.current_block_index] = self.current_image_index
        
        image_path = self._get_current_image()
        
        # Reset timer by invalidating old thread and starting new one
        self.remaining = block.duration
        self.block_start_time = time.time()
        
        # Increment thread ID to kill old timer and start fresh
        self._current_thread_id += 1
        thread_id = self._current_thread_id
        
        # Start new timer thread
        self._timer_thread = threading.Thread(
            target=self._timer_loop,
            args=(thread_id, block.duration),
            daemon=True
        )
        self._timer_thread.start()
        
        # Notify GUI with full block info to reset timer display
        if self.on_new_block:
            self.on_new_block(self.current_block_index, block, image_path)
    
    def previous_image(self):
        """Show previous image in global history and reset timer"""
        if self.state not in [SessionState.RUNNING, SessionState.PAUSED]:
            return
        
        block = self.session.blocks[self.current_block_index]
        if block.block_type != "pose":
            return  # Can't change images on break
        
        # Get the start index for this block
        block_start = self.block_start_indices.get(self.current_block_index, 0)
        
        # Go backward, skipping any None (break) images
        new_index = self.current_image_index - 1
        
        # Keep going back until we find a real image (not None) or hit block start
        while new_index >= block_start:
            if self.image_history[new_index] is not None:
                # Found a valid image
                self.current_image_index = new_index
                self.block_last_indices[self.current_block_index] = self.current_image_index
                
                image_path = self.image_history[self.current_image_index]
                
                # Reset timer by invalidating old thread and starting new one
                self.remaining = block.duration
                self.block_start_time = time.time()
                
                # Increment thread ID to kill old timer and start fresh
                self._current_thread_id += 1
                thread_id = self._current_thread_id
                
                # Start new timer thread
                self._timer_thread = threading.Thread(
                    target=self._timer_loop,
                    args=(thread_id, block.duration),
                    daemon=True
                )
                self._timer_thread.start()
                
                # Notify GUI with full block info to reset timer display
                if self.on_new_block:
                    self.on_new_block(self.current_block_index, block, image_path)
                return
            new_index -= 1
        
        # If we got here, there are no previous images in this block (do nothing)
    
    def skip_to_next_block(self):
        """Move to next block"""
        if self.state not in [SessionState.RUNNING, SessionState.PAUSED]:
            return
        
        if self.current_block_index >= len(self.session.blocks) - 1:
            return
        
        # Invalidate any running timer threads by incrementing ID
        self._current_thread_id += 1
        
        self.current_image_index = len(self.image_history)
        self._start_block(self.current_block_index + 1)
    
    def skip_to_previous_block(self):
        """Move to previous block"""
        if self.state not in [SessionState.RUNNING, SessionState.PAUSED]:
            return
        
        if self.current_block_index <= 0:
            return
        
        # Invalidate any running timer threads by incrementing ID
        self._current_thread_id += 1
        
        # Move to previous block
        prev_block_index = self.current_block_index - 1
        
        # Use the last viewed image position if we have one, otherwise use block start
        if prev_block_index in self.block_last_indices:
            self.current_image_index = self.block_last_indices[prev_block_index]
        elif prev_block_index in self.block_start_indices:
            self.current_image_index = self.block_start_indices[prev_block_index]
        else:
            self.current_image_index = 0
        
        self._start_block(prev_block_index)