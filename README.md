# CroquisCadence

<div align="center">

**A customizable figure drawing timer with smart session management**

![Version](https://img.shields.io/badge/version-1.2.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![Python](https://img.shields.io/badge/python-3.14-green)
![License](https://img.shields.io/badge/license-MIT-orange)

[Download Latest Release](../../releases/latest) • [Report Bug](../../issues) • [Request Feature](../../issues)

</div>

---

## Features

- **Smart Timer** - Smooth countdown with no skips, version-based thread sync
- **Session Builder** - Create custom practice sessions with pose blocks and breaks
- **Preset System** - Save and load your favorite session configurations
- **No Repeats** - Shows all images before repeating any
- **Image History** - Review and jump back to any pose from the current block
- **Dual Themes** - Cyberpunk and Matcha Latte (default) color schemes
- **Custom Sounds** - Adjustable volumes and custom .wav file support
- **⌨Keyboard Shortcuts** - Fully customizable controls
- **Fullscreen Mode** - Distraction-free drawing experience
- **Folder Organization** - Use subfolders to categorize references (hands, poses, anatomy, etc.)
- **NSFW Filtering** - Filter blocks to show only SFW, only NSFW, or all images
- **Live Tagging** - Right-click during session to tag/untag images as NSFW
- **Filter Badges** - Green `[SFW]`, Red `[NSFW]`, Blue `[ALL]` indicators in session builder
- **Customizable Warnings** - Warnings can be changes, added, removed, and recoloured

---

## Screenshots

> *Coming soon!*

---

## Quick Start

### Installation

1. Download the latest release: `CroquisCadence-v1.2.0-Windows.zip`
2. Extract the ZIP file to any folder
3. Run `CroquisCadence.exe`
4. On first launch, select your reference images folder

### Organizing Your Images

```
📁 YourReferenceFolder/
├── 📁 hands/
│   ├── hand_study_01.jpg
│   ├── hand_pose_nsfw.jpg
│   └── ...
├── 📁 full-body/
│   ├── standing_pose.png
│   ├── sitting_nsfw.png
│   └── ...
└── 📁 anatomy/
    └── ...
```

**NSFW Tagging:**
- Add `_nsfw` anywhere in the filename to mark as NSFW
- Example: `pose_nsfw_01.jpg` or `reference_001_nsfw.png`
- Or right-click during a session to tag/untag images

---

## Usage

### Creating a Session

1. Click **▶ START**
2. Enter a session name (optional)
3. Select folders from your reference collection
4. Add blocks:
   - **Pose Blocks** - Set duration, count, folders, and NSFW filter
   - **Break Blocks** - Rest periods between sets
5. Click **Start Session** or **Save as Preset**

### During a Session

**Keyboard Controls:**
- `←/→` or `A/D` - Previous/Next image
- `↑/↓` or `W/S` - Previous/Next block
- `Space` or `Enter` - Pause/Resume
- `F11` - Toggle fullscreen
- `Esc` - Exit fullscreen

**UI Controls:**
- **📜 History** - View all images from current block
- **⚙️ Settings** - Adjust volume, sounds, theme, shortcuts
- **Right-click image** - Tag/untag as NSFW
- **Assets** - Assets are all located in CroquisCadence/_internal/assets, which includes the break image and all transition and warning sounds! If you want to add your own, just put the .wav file in this folder!

---

## Themes

### Studio (Default)
Basic, professional setup so the UI won't affect colour perception of the references!

### Matcha Latte
Warm, calming aesthetic with green and cream tones

### Cyberpunk
Bold, vibrant aesthetic with pink, blue, and purple accents

Change themes in **Settings → Theme** (requires app restart)

### Create your own theme in the settings!!

### Customizable Warnings
- Warnings are now customizable, just go to the settings and choose at what percentage of the pose you want your warning to play
- Warning sounds and timer colour changes are also customizable in the settings!
- Add and remove warnings at wil

---

## Configuration

Settings are stored in the `settings/` folder:
- `app_settings.json` - General app settings
- `theme.json` - Current theme selection
- `volume.json` - Sound volume levels
- `sounds.json` - Custom sound file paths
- `session_presets.json` - Saved session presets

---

## Technical Details

### Built With
- **Python 3.14** - Core application
- **CustomTkinter** - Modern UI framework
- **PIL/Pillow** - Image processing
- **Threading** - Timer and async operations

### Supported Image Formats
JPG, JPEG, PNG, GIF, BMP

### System Requirements
- **OS:** Windows 10/11
- **RAM:** 100MB minimum
- **Storage:** Depends on your reference image collection

---

## Version History

### v1.2.0 (Current)
- ✨ NSFW/SFW content filtering system with per-block filters
- ✨ Live tagging via right-click during sessions  
- ✨ Image history viewer with clickable thumbnails
- ✨ Reference folder selection in Settings
- ✨ Colored filter badges in session builder (Green/Red/Blue)
- ✨ Customizable Warnings - Warnings can be changes, added, removed, and recoloured
- 🔧 Fixed timer synchronization - no more skipped numbers
- 🔧 Removed 500ms lag when skipping blocks
- 🔧 Auto-advance after tagging images
- 🔧 Complete cache synchronization for renamed files
- 🎨 Smart text color calculation for accessibility
- 🎨 Fixed-width session builder layout
- 🧹 Removed all debug code, production-ready

### v1.0.0
- Initial release
- Core timer functionality
- Session builder
- Keyboard shortcuts
- Sound effects

[Full Changelog](CHANGELOG.md)

---

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact

**ChisuyaSoo**
- GitHub: [@ChisuyaSoo](https://github.com/ChisuyaSoo)
- Issues: [Report a bug or request a feature](../../issues)

---

<div align="center">

**Enjoy your practice sessions!** 🎨✨

Made with ❤️ by ChisuyaSoo~

</div>
