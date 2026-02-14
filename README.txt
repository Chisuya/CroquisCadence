================================================================================
                        CroquisCadence - Figure Drawing Timer
================================================================================

Figure drawing software with class-type sessions that are fully customizable!

================================================================================
FEATURES
================================================================================

* No Repeated Images - Shows all images before repeating
* Image History Viewer - Review and revisit poses from current block
* Adjustable Sound Volume - Warning chime and transition sounds
* Custom Sound Files - Use your own sound effects
* Smart Timer - Automatically advances to next pose
* Keyboard Shortcuts - Fully customizable controls
* Fullscreen Mode - Distraction-free drawing
* Session Builder - Create custom practice sessions
* Preset Sessions - Save and load your favorite session configurations
* Theme Support - Choose between Cyberpunk and Matcha Latte themes
* Folder Tags - See which subfolder each image is from
* Session Naming - Name your sessions for better organization

================================================================================
HOW TO USE
================================================================================

--- FIRST TIME SETUP ---

1. Launch CroquisCadence.exe
   - On first launch, you'll be asked to select your reference images folder
   - Choose any folder on your computer that contains your images
   - You can organize images into subfolders (e.g., hands\, poses\, anatomy\)

--- CREATING A SESSION ---

1. Click the "Start" button
2. Enter a session name (optional - used when saving presets)
3. Choose folders with your reference images
4. Add blocks:
   - Pose blocks - Timed drawing sessions
   - Break blocks - Rest periods
5. Click "Start Session" or "Save as Preset" to reuse later

--- DURING A SESSION ---

Keyboard Controls:
* Arrow Keys (Left/Right) or A/D - Change image within block
* Arrow Keys (Up/Down) or W/S - Skip to next/previous block
* Enter or Space - Pause/Resume
* Escape - Exit fullscreen
* F11 - Toggle fullscreen

UI Controls:
* 📜 History Button - View all images from current block, click to revisit
* ⚙️ Settings Button - Adjust volume, sounds, theme, shortcuts
* ⛶ Fullscreen Button - Toggle fullscreen mode
* Folder Tag - Shows which subfolder the current image is from

--- SETTINGS ---

Click the Settings button (gear icon) to:
* Adjust sound volumes (warning and transition)
* Choose custom sound files (.wav format)
* Select theme (Cyberpunk or Matcha Latte)
* Customize keyboard shortcuts
* Change reference folder location

--- THEMES ---

CroquisCadence supports two beautiful themes:
* Cyberpunk - Dark with pink, blue, and purple accents
* Matcha Latte - Dark with warm greens and cream tones (default)

Change themes in Settings. Restart the app to see changes.

--- TIMER COLOR MEANINGS ---

Cyberpunk Theme:
* Pink = Normal time
* Pink = Warning zone (last 10% of block)

Matcha Latte Theme:
* Warm tan/cream = Normal time
* Bright orange = Warning zone (last 10% of block)

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
* Check that bell.wav and page_turn_stiff.wav exist in assets\ folder
* Adjust volume in Settings (might be set to 0%)
* You can choose custom sound files in Settings

Keyboard shortcuts not working?
* Open Settings and check/reset shortcuts
* Restart app after changing shortcuts

Theme not changing?
* Make sure to restart the app after changing themes
* Theme settings are saved in settings\theme.json

================================================================================
CHANGELOG
================================================================================

Version 1.1.0:
* Added theme system (Cyberpunk and Matcha Latte themes)
* Added image history viewer - click 📜 to see all poses from current block
* Added ability to jump back to previous images in history
* Added folder tags showing which subfolder each image is from
* Added session naming for better preset organization
* Added custom sound file selection
* Updated default sounds (bell.wav for warning, page_turn_stiff.wav for transition)
* Changed default transition volume to 100%
* Made Matcha Latte the default theme
* Improved timer color theming (theme-aware colors)
* All UI elements now respect theme colors

Version 1.0.0:
* Initial release
* Core timer functionality
* Session builder with custom blocks
* Keyboard shortcuts
* Sound effects
* Fullscreen mode

================================================================================

Created for artists who want to use their own reference photos for 
figure drawing practice!

Enjoy your practice sessions!

- ChisuyaSoo

================================================================================
