from enum import Enum
from typing import Callable, Optional, List
import threading
import time

class TimerState(Enum):
    """Possible states of the timer"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"

class TimerController:
    """
    Manages timing logic for drawing sessions.
    Uses threading to not block the GUI.
    """
    
    def __init__(self):
        """Initialize the timer controller"""
        self.state = TimerState.IDLE
        self.duration: int = 0
        self.remaining: int = 0
        
        # Thread management
        self._timer_thread: Optional[threading.Thread] = None
        self._stop_flag = threading.Event()
        self._pause_flag = threading.Event()
        
        # Callbacks
        self.on_tick: Optional[Callable[[int], None]] = None
        self.on_complete: Optional[Callable[[], None]] = None
        self.on_interval_ping: Optional[Callable[[int], None]] = None
    
    def start(self, duration: int, interval_pings: Optional[List[int]] = None):
        """
        Start countdown timer
        
        :param duration: Duration in seconds
        :param interval_pings: Optional list of times to ping at
        """
        # If there's already a thread running, stop it and wait
        if self._timer_thread and self._timer_thread.is_alive():
            # Don't try to join if we're in the same thread
            if self._timer_thread != threading.current_thread():
                self._stop_flag.set()
                self._timer_thread.join(timeout=0.5)  # Wait briefly
        
        self._stop_flag.clear()
        self._pause_flag.clear()
        
        self.duration = duration
        self.remaining = duration
        self.state = TimerState.RUNNING
        
        interval_list = interval_pings if interval_pings else []
        self._timer_thread = threading.Thread(
            target=self._timer_loop,
            args=(interval_list,),
            daemon=True
        )
        self._timer_thread.start()
    
    def pause(self):
        """Pause the current timer"""
        if self.state == TimerState.RUNNING:
            self._pause_flag.set()
            timeout = 2.0
            start = time.time()
            while self.state != TimerState.PAUSED and (time.time() - start) < timeout:
                time.sleep(0.1)

    def resume(self):
        """Resume a paused timer"""
        if self.state == TimerState.PAUSED:
            self._pause_flag.clear()
    
    def stop(self, wait=True):
        """Stop and reset the timer"""
        self._stop_flag.set()
        self.state = TimerState.IDLE
        self.remaining = 0

        if wait and self._timer_thread and self._timer_thread.is_alive():
            self._timer_thread.join(timeout=2.0)
    
    def _timer_loop(self, interval_pings: List[int]):
        """The actual timer logic (runs in separate thread)"""
        pings_triggered = set()

        while self.remaining > 0:
            if self._stop_flag.is_set():
                break

            if self._pause_flag.is_set():
                self.state = TimerState.PAUSED

                while self._pause_flag.is_set():
                    if self._stop_flag.is_set():
                        break
                    time.sleep(0.1)

                if self._stop_flag.is_set():
                    break

                self.state = TimerState.RUNNING

            time.sleep(1)

            self.remaining -= 1

            if self.remaining in interval_pings and self.remaining not in pings_triggered:
                pings_triggered.add(self.remaining)
                if self.on_interval_ping:
                    self.on_interval_ping(self.remaining)
            
            if self.on_tick:
                self.on_tick(self.remaining)
            
        if not self._stop_flag.is_set():
            self.state = TimerState.COMPLETED
            if self.on_complete:
                self.on_complete()
        else:
            self.state = TimerState.IDLE