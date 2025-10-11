# Universal Video & Audio Downloader Pro 2.0

A powerful, feature-rich desktop application for downloading videos and audio from multiple platforms with a modern GUI interface.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🌟 Features

### Multi-Platform Support
Download content from:
- **YouTube** (videos, playlists, live streams)
- **YouTube Music** (audio optimization)
- **Instagram** (posts, reels, stories)
- **Facebook** (videos, live streams)
- **TikTok** (videos, live streams)
- **Twitter/X** (videos, threads)
- **Kick** (VODs, clips, live streams)
- **Twitch** (VODs, clips, live streams)
- **Vimeo** (videos)
- **Dailymotion** (videos)
- **SoundCloud** (tracks, playlists)
- **Reddit** (videos)
- And more generic URLs!

### Download Options
- **Video Downloads**
  - Multiple quality options: 2160p, 1440p, 1080p, 720p, 480p, 360p, or highest available
  - Automatic format selection (MP4)
  - Merges video and audio streams for best quality
  
- **Audio-Only Downloads**
  - Multiple format options: MP3, M4A, OPUS, FLAC, or best available
  - High-quality audio extraction (up to 320kbps)
  - Automatic metadata embedding
  - Thumbnail embedding for MP3/M4A files

### User Interface
- **Modern GUI** with clean, intuitive design
- **Ultra-smooth progress bar** with 120fps animation
- **Real-time progress tracking** with download size display
- **Platform auto-detection** from pasted URLs
- **Clipboard monitoring** - automatically detects URLs from clipboard
- **Drag-and-drop support** (optional, requires tkinterdnd2)
- **Configuration persistence** - remembers your settings

### Advanced Features
- **Playlist support** for YouTube, SoundCloud, and YouTube Music
- **Live stream recording** for supported platforms
- **Multi-threaded downloads** for optimal performance
- **Instant stop functionality** with aggressive process termination
- **Special Kick.com handling** with optimized streaming options
- **Automatic retry** on network failures
- **Fragment recovery** for interrupted downloads
- **Custom headers** to bypass restrictions

## 📋 Requirements

### Python Dependencies
```
python >= 3.7
yt-dlp >= 2023.0.0
psutil
tkinter (usually comes with Python)
tkinterdnd2 (optional, for drag-and-drop)
```

### External Dependencies
- **FFmpeg** - Required for video/audio conversion and merging
  - Download from: https://ffmpeg.org/download.html
  - Must be in system PATH or same directory as script

## 🚀 Installation

### 1. Clone or Download
```bash
git clone <repository-url>
cd video_downloader
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install yt-dlp psutil
pip install tkinterdnd2  # Optional, for drag-and-drop
```

### 3. Install FFmpeg

#### Windows
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add `C:\ffmpeg\bin` to system PATH

#### macOS
```bash
brew install ffmpeg
```

#### Linux
```bash
sudo apt install ffmpeg  # Ubuntu/Debian
sudo dnf install ffmpeg  # Fedora
```

### 4. Run the Application
```bash
python video_downloader.py
```

## 💻 Usage

### Basic Usage
1. **Launch the application**
   ```bash
   python video_downloader.py
   ```

2. **Enter or paste a video URL**
   - The platform will be auto-detected
   - Or copy a URL to clipboard (it will be auto-detected)

3. **Select download type**
   - Choose between Video or Audio Only

4. **Choose quality/format**
   - For videos: Select quality (highest, 2160p, 1440p, 1080p, 720p, 480p, 360p)
   - For audio: Select format (MP3, M4A, OPUS, FLAC, or best)

5. **Select download location**
   - Browse to your preferred folder
   - Default: `~/Downloads`

6. **Click Download**
   - Watch the progress bar for real-time updates
   - Stop anytime with the Stop button

### Advanced Usage

#### Command-Line Integration
```python
from video_downloader import DownloadManager

# Create download manager
manager = DownloadManager()

# Download video
success, message = manager.download(
    url="https://youtube.com/watch?v=...",
    output_path="/path/to/downloads",
    download_type='video',
    quality='1080p'
)

# Download audio
success, message = manager.download(
    url="https://soundcloud.com/...",
    output_path="/path/to/downloads",
    download_type='audio',
    audio_format='mp3'
)
```

#### Platform Detection
```python
from video_downloader import PlatformDetector

# Detect platform
platform_id, platform_info = PlatformDetector.detect(url)
print(f"Platform: {platform_info['name']}")
print(f"Supports playlists: {platform_info['supports_playlist']}")
print(f"Live support: {platform_info['live_support']}")

# Check if playlist
is_playlist = PlatformDetector.is_playlist(url)
```

## 🎯 Features Explained

### Platform Detection
The application automatically detects the source platform and optimizes download settings:
- **YouTube**: Full quality options, playlist support
- **Instagram**: Automatic cookie handling for private content
- **TikTok**: Optimized for TikTok video format
- **Kick**: Special handling for live streams and VODs
- **Twitter/X**: Protocol filtering for best compatibility

### Download Management
- **Threading**: Downloads run in background threads for responsive UI
- **Progress Tracking**: Real-time progress with byte-level accuracy
- **Smart Stopping**: Immediate termination with process cleanup
- **Error Handling**: Comprehensive error messages with recovery suggestions

### Smooth Progress Bar
- **120fps Animation**: Ultra-smooth progress updates
- **Dynamic Easing**: Adaptive animation speed based on progress
- **Visual Feedback**: Instant UI response for better UX

### Configuration Persistence
Settings are saved to `~/.video_downloader_config.json`:
```json
{
  "download_path": "/path/to/downloads",
  "download_type": "video",
  "video_quality": "720p",
  "audio_format": "mp3"
}
```

## 🛠️ Architecture

### Class Structure

#### `PlatformDetector`
- Handles URL validation and platform identification
- Maintains platform database with patterns and capabilities
- Provides playlist detection

#### `DownloadManager`
- Core download logic with yt-dlp integration
- Progress callback system
- Thread-safe download management
- Special handling for different platforms

#### `YouTubeDownloader`
- Main GUI application class
- UI setup and event handling
- Configuration management
- Clipboard monitoring
- Smooth animation system

### Key Methods

```python
# Download control
download()                    # Start download with full options
stop_download()              # Immediate stop with cleanup
reset()                      # Reset download state

# UI updates
on_progress(d)               # Handle yt-dlp progress hooks
on_status_update(message)    # Update status messages
_animate_progress()          # Smooth progress bar animation

# Configuration
load_config()                # Load saved settings
save_config()                # Persist current settings
```

## ⚙️ Configuration Options

### Video Quality Options
| Option | Resolution | Use Case |
|--------|-----------|----------|
| `highest` | Best available | Maximum quality |
| `2160p` | 4K | Ultra HD displays |
| `1440p` | 2K | High-end monitors |
| `1080p` | Full HD | Standard HD |
| `720p` | HD | Balanced quality/size |
| `480p` | SD | Smaller files |
| `360p` | Low | Limited bandwidth |

### Audio Format Options
| Format | Quality | File Size | Compatibility |
|--------|---------|-----------|---------------|
| `mp3` | High (320kbps) | Medium | Universal |
| `m4a` | Very High | Medium-Small | Apple devices |
| `opus` | Very High | Small | Modern players |
| `flac` | Lossless | Large | Audiophiles |
| `best` | Original | Varies | Best available |

## 🐛 Troubleshooting

### Common Issues

#### "FFmpeg not found"
**Solution**: Install FFmpeg and add to system PATH
```bash
# Check if FFmpeg is installed
ffmpeg -version
```

#### "Could not extract video information"
**Solutions**:
1. Check if URL is valid and accessible
2. Try updating yt-dlp: `pip install -U yt-dlp`
3. Some content may require login cookies

#### "Download failed: 403 Forbidden"
**Solutions**:
1. Content may be private or geo-restricted
2. For Instagram/Facebook, try logging in to browser first
3. The application will attempt to use browser cookies

#### "Live stream has ended"
**Solution**: Live streams can only be downloaded while active

#### Download is slow
**Solutions**:
1. Check your internet connection
2. Try a lower quality setting
3. The platform may be rate-limiting

### Platform-Specific Issues

#### Kick.com Downloads
- Live streams download in real-time (may be lengthy)
- VODs and clips work like regular downloads
- Requires active stream for live content

#### Instagram/Facebook
- May require browser cookies for private content
- Application attempts to use Chrome cookies automatically
- Login to Chrome first for best results

#### TikTok
- Sometimes shortened URLs need expansion
- Try using full TikTok URL format

## 🔒 Privacy & Security

- **No Data Collection**: All downloads are local
- **Cookie Handling**: Uses local browser cookies only when needed
- **No Account Required**: Works with public content
- **Source Code**: Fully transparent and auditable

## 📝 License

This project is provided for educational purposes. Users are responsible for complying with the terms of service of the platforms they download from.

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional platform support
- UI enhancements
- Performance optimizations
- Bug fixes and error handling
- Documentation improvements

## 📞 Support

For issues and questions:
1. Check the Troubleshooting section
2. Update yt-dlp: `pip install -U yt-dlp`
3. Verify FFmpeg installation
4. Check platform-specific notes

## 🔄 Updates

### Version 2.0 Features
- ✅ Multi-platform support (12+ platforms)
- ✅ Ultra-smooth 120fps progress bar
- ✅ Instant stop functionality
- ✅ Clipboard monitoring
- ✅ Platform auto-detection
- ✅ Configuration persistence
- ✅ Special Kick.com handling
- ✅ Playlist support
- ✅ Live stream recording

## 🌐 Supported URL Examples

```
# YouTube
https://youtube.com/watch?v=...
https://youtu.be/...
https://music.youtube.com/...

# Instagram
https://instagram.com/p/...
https://instagram.com/reel/...

# TikTok
https://tiktok.com/@user/video/...
https://vm.tiktok.com/...

# Twitter/X
https://twitter.com/user/status/...
https://x.com/user/status/...

# Kick
https://kick.com/username
https://kick.com/username/video/...

# Twitch
https://twitch.tv/username
https://clips.twitch.tv/...

# Facebook
https://facebook.com/watch/?v=...
https://fb.watch/...

# And many more!
```

## ⚡ Performance Tips

1. **Use appropriate quality**: Higher quality = larger files and slower downloads
2. **Close other apps**: Free up bandwidth for faster downloads
3. **SSD storage**: Faster write speeds improve download performance
4. **Update regularly**: Keep yt-dlp updated for best compatibility
5. **Stable connection**: Wired connection recommended for large downloads

## 🎨 UI Features

- **Responsive Design**: Adjusts to window resizing
- **Theme Support**: Uses system theme colors
- **Status Indicators**: Clear visual feedback for all states
- **Progress Details**: Shows download size and percentage
- **Platform Icons**: Visual indicators for detected platforms
- **Smooth Animations**: Professional, fluid UI transitions

---

**Made with ❤️ for content creators and enthusiasts**

*Remember to respect copyright and terms of service when downloading content!*

