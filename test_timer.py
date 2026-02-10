# test_timer.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from controllers.timer_controller import TimerController, TimerState
import time

def test_basic_countdown():
    """Test basic countdown functionality"""
    print("Testing basic countdown...")
    
    timer = TimerController()
    
    # Register callbacks
    def on_tick(remaining):
        print(f"  Tick: {remaining}s remaining")
    
    def on_complete():
        print("Timer completed!")
    
    def on_ping(remaining):
        print(f"PING at {remaining}s!")
    
    timer.on_tick = on_tick
    timer.on_complete = on_complete
    timer.on_interval_ping = on_ping
    
    # Start 5-second timer with ping at 2s
    print("Starting 5-second timer...")
    timer.start(duration=5, interval_pings=[2])
    
    # Wait for it to finish
    time.sleep(6)
    
    assert timer.state == TimerState.COMPLETED
    print("Basic countdown test passed!\n")

def test_pause_resume():
    """Test pause and resume"""
    print("Testing pause/resume...")
    
    timer = TimerController()
    
    def on_tick(remaining):
        print(f"  {remaining}s")
    
    timer.on_tick = on_tick
    
    print("Starting 10-second timer...")
    timer.start(duration=10)
    
    time.sleep(3)
    print("Pausing...")
    timer.pause()
    
    assert timer.state == TimerState.PAUSED
    time.sleep(2)  # Wait while paused
    
    print("Resuming...")
    timer.resume()
    
    time.sleep(3)
    print("Stopping...")
    timer.stop()
    
    assert timer.state == TimerState.IDLE
    print("Pause/resume test passed!\n")

if __name__ == "__main__":
    test_basic_countdown()
    test_pause_resume()
    print("ALL TESTS PASSED!")
