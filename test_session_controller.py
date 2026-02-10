import time
from pathlib import Path

from models.session import Session, SessionBlock
from models.image_collection import ImageCollection
from controllers.session_controller import SessionController, SessionState

# Test data paths
TEST_BASE_PATH = Path("test_data/references")


def test_single_block_session():
    """Test a simple session with one pose block"""
    # ... (your existing test stays here)


def test_multi_block_session():
    """Test session with multiple blocks (pose -> break -> pose)"""
    print("\n=== Test: Multi-Block Session ===")
    
    # Setup
    collection = ImageCollection(TEST_BASE_PATH)
    controller = SessionController(collection)
    
    # Create session with 3 blocks: pose → break → pose
    session = Session(
        name="Multi-Block Test",
        blocks=[
            SessionBlock(block_type="pose", duration=2, count=1, folder_paths=None),
            SessionBlock(block_type="break", duration=1, count=1),
            SessionBlock(block_type="pose", duration=2, count=1, folder_paths=None),
        ]
    )
    
    # Track all blocks that started
    blocks_started = []
    images_shown = []
    
    def on_new_block_handler(block_index, block, image_path):
        print(f"  -> Block #{block_index}: {block.block_type}")
        if image_path:
            print(f"     Image: {image_path.name}")
        blocks_started.append(block_index)
        images_shown.append(image_path)
    
    session_completed = False
    def on_session_end_handler():
        nonlocal session_completed
        print("  -> All blocks complete!")
        session_completed = True
    
    controller.on_new_block = on_new_block_handler
    controller.on_session_end = on_session_end_handler
    
    # Start and wait
    print("Starting multi-block session...")
    controller.start(session)
    time.sleep(6)  # 2s + 1s + 2s + buffer
    
    # Verify all 3 blocks started
    assert len(blocks_started) == 3, f"Should start 3 blocks, got {len(blocks_started)}"
    assert blocks_started == [0, 1, 2], f"Blocks should be in order, got {blocks_started}"
    
    # Verify images: pose blocks have images, break doesn't
    assert images_shown[0] is not None, "First pose should have image"
    assert images_shown[1] is None, "Break should not have image"
    assert images_shown[2] is not None, "Second pose should have image"
    
    # Verify different images (exclusion working)
    if len(collection.images) > 1:  # Only test if multiple images available
        assert images_shown[0] != images_shown[2], "Should show different images!"
    
    # Verify session completed
    assert session_completed, "Session should complete"
    assert controller.state == SessionState.COMPLETED, "Should be COMPLETED"
    
    print("Multi-block test passed!")


def test_pause_resume():
    """Test pausing and resuming a session"""
    print("\n=== Test: Pause/Resume ===")
    
    # Setup
    collection = ImageCollection(TEST_BASE_PATH)
    controller = SessionController(collection)
    
    # Create a 5-second session
    session = Session(
        name="Pause Test",
        blocks=[
            SessionBlock(block_type="pose", duration=5, count=1, folder_paths=None)
        ]
    )
    
    tick_count = 0
    def on_tick_handler(remaining):
        nonlocal tick_count
        tick_count += 1
        print(f"  -> Tick: {remaining}s")
    
    controller.on_tick = on_tick_handler
    
    # Start session
    print("Starting session...")
    controller.start(session)
    assert controller.state == SessionState.RUNNING
    
    # Let it run for 2 seconds
    time.sleep(2)
    initial_ticks = tick_count
    print(f"Ticks after 2s: {initial_ticks}")
    
    # Pause
    print("Pausing...")
    controller.pause()
    assert controller.state == SessionState.PAUSED
    ticks_at_pause = tick_count
    
    # Wait 2 seconds while paused (should not tick)
    time.sleep(2)
    print(f"Ticks after pause: {tick_count}")
    assert tick_count == ticks_at_pause, "Should not tick while paused!"
    
    # Resume
    print("Resuming...")
    controller.resume()
    assert controller.state == SessionState.RUNNING
    
    # Let it finish
    time.sleep(4)
    
    # Should have ticked more after resuming
    print(f"Final tick count: {tick_count}")
    assert tick_count > ticks_at_pause, "Should tick after resume"
    
    print("Pause/resume test passed!")


def test_stop_mid_session():
    """Test stopping a session in the middle"""
    print("\n=== Test: Stop Mid-Session ===")
    
    # Setup
    collection = ImageCollection(TEST_BASE_PATH)
    controller = SessionController(collection)
    
    # Create a long session
    session = Session(
        name="Stop Test",
        blocks=[
            SessionBlock(block_type="pose", duration=10, count=1, folder_paths=None)
        ]
    )
    
    session_completed = False
    def on_session_end_handler():
        nonlocal session_completed
        session_completed = True
    
    controller.on_session_end = on_session_end_handler
    
    # Start session
    print("Starting session...")
    controller.start(session)
    assert controller.state == SessionState.RUNNING
    
    # Let it run briefly
    time.sleep(2)
    
    # Stop it
    print("Stopping mid-session...")
    controller.stop()
    
    # Verify state reset
    assert controller.state == SessionState.IDLE, "Should be IDLE after stop"
    assert controller.session is None, "Session should be cleared"
    assert controller.current_block_index == 0, "Block index should reset"
    assert controller.last_image is None, "Last image should be cleared"
    
    # Session end callback should NOT fire when stopped
    time.sleep(1)
    assert not session_completed, "session_end should not fire on manual stop"
    
    print("Stop test passed!")


def test_cannot_start_twice():
    """Test that starting an already-running session raises error"""
    print("\n=== Test: Cannot Start Twice ===")
    
    # Setup
    collection = ImageCollection(TEST_BASE_PATH)
    controller = SessionController(collection)
    
    session = Session(
        name="Double Start Test",
        blocks=[
            SessionBlock(block_type="pose", duration=5, count=1, folder_paths=None)
        ]
    )
    
    # Start once
    controller.start(session)
    assert controller.state == SessionState.RUNNING
    
    # Try to start again - should raise error
    try:
        controller.start(session)
        assert False, "Should have raised ValueError!"
    except ValueError as e:
        print(f"  Correctly raised error: {e}")
    
    # Clean up
    controller.stop()
    
    print("Double-start prevention test passed!")


# ================================
# RUN ALL TESTS
# ================================

if __name__ == "__main__":
    print("=" * 50)
    print("RUNNING ALL SESSION CONTROLLER TESTS")
    print("=" * 50)
    
    test_single_block_session()
    test_multi_block_session()
    test_pause_resume()
    test_stop_mid_session()
    test_cannot_start_twice()
    
    print("\n" + "=" * 50)
    print("ALL TESTS PASSED!")
    print("=" * 50)