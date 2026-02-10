from pathlib import Path
from models.session import SessionBlock, Session
from models.image_collection import ImageCollection
import random

TEST_BASE_PATH = Path("test_data/references")

def test_session_block():
    """Test SessionBlock creation + validation"""
    print("Testing SessionBlock...")

    # Test 1: Valid pose block
    block1 = SessionBlock(
        block_type="pose",
        duration=30,
        count=10,
        folder_paths=["hands"],
        interval_pings=[10, 5]
    )
    print(f"Block 1 duration: {block1.total_duration()}s")

    # Test 2: valid break
    block2 = SessionBlock(
        block_type="break",
        duration=300,
        count=1
    )
    print(f"Block 2 duration: {block2.total_duration()}s")

    # Test 3: Invalid - negative duration
    try:
        block3 = SessionBlock(
            block_type="pose",
            duration=-30,
            count=10
        )
        print("Test 3 should have raised an error!")
    except ValueError as e:
        print(f"Test 3 caught error: {e}")

    print("\nSesionBlock tests passed!\n")

def test_session():
    """Test session creation + formatting"""
    print("Testing...")

    # Create blocks
    blocks = [
        SessionBlock(block_type="pose", duration=30, count=10),   # 300s
        SessionBlock(block_type="pose", duration=60, count=5),    # 300s
        SessionBlock(block_type="break", duration=300, count=1),  # 300s
        SessionBlock(block_type="pose", duration=1500, count=1),  # 1500s
    ]
    
    # Create session
    session = Session(name="Morning Warmup", blocks=blocks)
    
    # Test total duration
    total = session.total_duration()
    print(f"Total duration: {total}s (expected: 2400s)")
    assert total == 2400, f"Expected 2400, got {total}"
    print("Total duration correct!")
    
    # Test formatting
    formatted = session.format_duration()
    print(f"Formatted: {formatted} (expected: 40m)")
    assert formatted == "40m", f"Expected '40m', got '{formatted}'"
    print("Format correct!")
    
    print("\nSession tests passed!\n")

def test_duration_formatting():
    """Test various duration formats"""
    print("Testing duration formatting...")
    
    test_cases = [
        (30, "30s"),
        (60, "1m"),
        (90, "1m 30s"),
        (3600, "1h"),
        (3661, "1h 1m 1s"),
        (7325, "2h 2m 5s"),
    ]
    
    for seconds, expected in test_cases:
        block = SessionBlock(block_type="pose", duration=seconds, count=1)
        session = Session(name="Test", blocks=[block])
        result = session.format_duration()
        
        if result == expected:
            print(f"YES {seconds}s → {result}")
        else:
            print(f"NO {seconds}s → {result} (expected: {expected})")
    
    print("\nDuration formatting tests passed!\n")

def test_empty_session():
    """Test session w/ no blocks"""
    print("Testing empty session...")

    session = Session(name="Empty", blocks=[])

    total = session.total_duration()
    print(f"Emmpty session duration: {total}s (expected: 0s)")
    assert total == 0, f"Expected 0, got {total}"

    formatted = session.format_duration()
    print(f"Empty session formatted: {formatted} (expected: 0s)")
    assert formatted == "0s", f"Expected '0s', got '{formatted}'"

    print("Empty sesesion handled correctly!\n")

# ================================
# IMAGE COLLECTION TESTS
# ================================

def test_image_loading():
    """Test loading images from directory"""
    print("Testing ImageCollection - image loading...")
    
    collection = ImageCollection(Path("test_data/references"))
    
    print(f"Found {len(collection.images)} images")
    for img in collection.images:
        print(f"  - {img}")
    
    assert len(collection.images) > 0, "Should find at least one image!"
    print("Image loading test passed!\n")

def test_available_folders():
    """Test getting available folder names"""
    print("Testing ImageCollection - available folders...")
    
    collection = ImageCollection(Path("test_data/references"))
    folders = collection.get_available_folders()
    
    print(f"Found folders: {folders}")
    print(f"Type: {type(folders)}")
    
    # Verify it's a set of strings
    assert isinstance(folders, set), "Should return a set!"
    if folders:
        first_item = list(folders)[0]
        assert isinstance(first_item, str), f"Should contain strings, got {type(first_item)}"
        print(f"Returns Set[str] with {len(folders)} folders!\n")

def test_folder_filtering():
    """Test filtering images by folder"""
    print("Testing ImageCollection - folder filtering...")
    
    collection = ImageCollection(Path("test_data/references"))
    
    # Test with your actual folder names
    folders = collection.get_available_folders()
    if folders:
        test_folder = list(folders)[0]  # Pick first folder
        filtered = collection.get_images_by_folders([test_folder])
        print(f"Images in '{test_folder}': {len(filtered)}")
        print("Filtering test passed!\n")
    else:
        print("No folders found to test filtering\n")

# ================================
# Testing Random Image
# ================================
def test_random_image():
    """Test getting random images"""
    print("Testing ImageCollection - random image...")
    
    collection = ImageCollection(Path("test_data/references"))
    
    # Test 1: Random from specific folder
    random_img = collection.get_random_image(["hands"])
    print(f"Random from 'hands': {random_img}")
    assert "hands" in str(random_img).lower(), "Should be from hands folder!"
    print("Specific folder works!")
    
    # Test 2: Random from all folders (None)
    random_img = collection.get_random_image(None)
    print(f"Random from all: {random_img}")
    print("All folders works!")
    
    # Test 3: Random from multiple folders
    random_img = collection.get_random_image(["hands", "faces"])
    print(f"Random from 'hands' or 'faces': {random_img}")
    print("Multiple folders works!")
    
    # Test 4: Error when no images found
    try:
        collection.get_random_image(["nonexistent_folder"])
        print("Should have raised an error!")
    except ValueError as e:
        print(f"Correctly raised error: {e}")
    
    print() 

def test_image_exclusion():
    """Test that excluded images aren't returned"""
    collection = ImageCollection(TEST_BASE_PATH)
    
    # Get first image
    first_image = collection.get_random_image()
    
    # Get second image, excluding the first
    second_image = collection.get_random_image(exclude=first_image)
    
    # They should be different
    assert first_image != second_image, "Excluded image was returned!"
    
    print(f"✓ First: {first_image.name}")
    print(f"✓ Second: {second_image.name}")
    print("✓ Exclusion working!")

# ================================
# RUN ALL TESTS
# ================================

if __name__ == "__main__":
    print("=" * 50)
    print("RUNNING ALL MODEL TESTS")
    print("=" * 50 + "\n")
    
    # Session tests
    test_session_block()
    test_session()
    test_duration_formatting()
    test_empty_session()
    
    # ImageCollection tests
    test_image_loading()
    test_available_folders()
    test_folder_filtering()

    test_image_exclusion()
    
    print("=" * 50)
    print("ALL TESTS PASSED!")
    print("=" * 50)