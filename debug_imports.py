# debug_imports.py

import sys
from pathlib import Path

print("=" * 50, flush=True)
print("=== IMPORT DEBUG STARTING ===", flush=True)
print("=" * 50, flush=True)

print(f"\nCurrent file: {__file__}", flush=True)
print(f"Parent directory: {Path(__file__).parent}", flush=True)

print("\nPython path:", flush=True)
for p in sys.path:
    print(f"  {p}", flush=True)

# Check if controllers exists
controllers_path = Path(__file__).parent / "controllers"
print(f"\nControllers path: {controllers_path}", flush=True)
print(f"Controllers exists: {controllers_path.exists()}", flush=True)
print(f"Controllers is directory: {controllers_path.is_dir()}", flush=True)

# Check __init__.py
init_path = controllers_path / "__init__.py"
print(f"\n__init__.py path: {init_path}", flush=True)
print(f"__init__.py exists: {init_path.exists()}", flush=True)

# Check timer_controller.py
timer_path = controllers_path / "timer_controller.py"
print(f"\ntimer_controller.py path: {timer_path}", flush=True)
print(f"timer_controller.py exists: {timer_path.exists()}", flush=True)

# List all files in controllers
print(f"\nFiles in controllers/:", flush=True)
if controllers_path.exists():
    for item in controllers_path.iterdir():
        print(f"  {item.name}", flush=True)

# Try to import
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "=" * 50, flush=True)
print("ATTEMPTING IMPORTS...", flush=True)
print("=" * 50, flush=True)

try:
    import controllers
    print("Successfully imported 'controllers' package", flush=True)
except Exception as e:
    print(f"Failed to import 'controllers': {e}", flush=True)

try:
    from controllers import timer_controller
    print("Successfully imported 'timer_controller' module", flush=True)
except Exception as e:
    print(f"Failed to import 'timer_controller': {e}", flush=True)

try:
    from controllers.timer_controller import TimerController, TimerState
    print("Successfully imported 'TimerController' class", flush=True)
    print(f"   TimerState: {TimerState}", flush=True)
except Exception as e:
    print(f"Failed to import 'TimerController': {e}", flush=True)
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50, flush=True)
print("=== DEBUG COMPLETE ===", flush=True)
print("=" * 50, flush=True)