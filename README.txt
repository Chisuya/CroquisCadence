================================================================================
                        CroquisCadence - Figure Drawing Timer
================================================================================

Figure drawing software with class-type sessions that are fully customizable!

================================================================================
FEATURES
================================================================================

* No Repeated Images - Shows all images before repeating
* Adjustable Sound Volume - Warning chime and transition sounds
* Smart Timer - Automatically advances to next pose
* Keyboard Shortcuts - Fully customizable controls
* Fullscreen Mode - Distraction-free drawing
* Session Builder - Create custom practice sessions

================================================================================
HOW TO USE
================================================================================

--- FIRST TIME SETUP ---

1. Launch CroquisCadence.exe
   - On first launch, you'll be asked to select your reference images folder
   - Choose any folder on your computer that contains your images
   - You can organize images into subfolders (e.g., hands\, poses\, anatomy\)

2. Add Sound Files (Optional)
   - Place warning.wav in assets\ folder (plays when time is running out)
   - Place transition.wav in assets\ folder (plays when changing poses)

--- CREATING A SESSION ---

1. Click the "Start" button
2. Choose folders with your reference images
3. Add blocks:
   - Pose blocks - Timed drawing sessions
   - Break blocks - Rest periods
4. Click "Start Session"

--- DURING A SESSION ---

Keyboard Controls:
* Arrow Keys (Left/Right) or A/D - Change image within block
* Arrow Keys (Up/Down) or W/S - Skip to next/previous block
* Enter or Space - Pause/Resume
* Escape - Exit fullscreen
* F11 - Toggle fullscreen

--- SETTINGS ---

Click the Settings button (gear icon) to:
* Adjust sound volumes
* Customize keyboard shortcuts
* Configure preferences

================================================================================
FOLDER STRUCTURE
================================================================================

CroquisCadence\
├── CroquisCadence.exe       <-- Run this!
├── README.txt               (this file)
├── assets\
│   ├── break_image.png      (default break screen)
│   ├── warning.wav          (add your own)
│   └── transition.wav       (add your own)
└── settings\
    ├── app_settings.json    (stores reference folder path)
    ├── keyboard_shortcuts.json
    └── volume.json

Your reference images can be ANYWHERE on your computer!
Just select the folder on first launch.

================================================================================
SOUND FILES
================================================================================

Free sound resources:
* Freesound.org
* Mixkit.co/free-sound-effects
* Zapsplat.com

Search for:
* "soft chime" or "bell" for warning sound
* "click" or "whoosh" for transition sound

Keep sounds short (less than 1 second) and subtle!

================================================================================
TIPS
================================================================================

Timer Colors:
* Pink = Normal time
* Red = Last 10% of block (warning zone)

Best Practices:
* Start with short sessions (5-10 minutes)
* Mix different pose durations (30s, 1m, 5m)
* Take breaks between blocks
* Use fullscreen for focus

================================================================================
TROUBLESHOOTING
================================================================================

Images not showing?
* Make sure you selected a folder with image subfolders
* Supported formats: JPG, PNG, JPEG, GIF, BMP
* Change folder in Settings if needed

Want to change reference folder?
* Open Settings (gear icon)
* Click "Change Folder" in Reference Folder section
* Restart the app

No sound?
* Check that warning.wav and transition.wav exist in assets\ folder
* Adjust volume in Settings (might be set to 0%)

Keyboard shortcuts not working?
* Open Settings and check/reset shortcuts
* Restart app after changing shortcuts

================================================================================

Created for artists who want a distraction-free figure drawing practice tool.

Enjoy your practice sessions!

================================================================================
