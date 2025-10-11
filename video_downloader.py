"""
Universal Video & Audio Downloader Pro
Supports: YouTube, Instagram, Facebook, TikTok, Twitter/X, Kick, Twitch, and more
Fixed and refactored version with complete platform support
"""

import os
import sys
import subprocess
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
from threading import Thread, Lock, Event
from datetime import datetime
import re
import json
import time
import traceback
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import queue
import signal
import psutil

# Core downloader library
try:
    import yt_dlp
except ImportError:
    print("Installing yt-dlp...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"])
    import yt_dlp

# Optional drag-and-drop support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False
    print("Note: tkinterdnd2 not installed. Drag-and-drop disabled.")


class PlatformDetector:
    """Handles URL validation and platform detection"""
    
    PLATFORMS = {
        'youtube': {
            'patterns': [r'youtube\.com', r'youtu\.be'],
            'name': 'YouTube',
            'supports_playlist': True,
            'live_support': True
        },
        'youtube_music': {
            'patterns': [r'music\.youtube\.com'],
            'name': 'YouTube Music',
            'supports_playlist': True,
            'live_support': False
        },
        'instagram': {
            'patterns': [r'instagram\.com', r'instagr\.am'],
            'name': 'Instagram',
            'supports_playlist': False,
            'live_support': False
        },
        'facebook': {
            'patterns': [r'facebook\.com', r'fb\.watch', r'fb\.com'],
            'name': 'Facebook',
            'supports_playlist': False,
            'live_support': True
        },
        'tiktok': {
            'patterns': [r'tiktok\.com', r'vm\.tiktok\.com'],
            'name': 'TikTok',
            'supports_playlist': False,
            'live_support': True
        },
        'twitter': {
            'patterns': [r'twitter\.com', r'x\.com'],
            'name': 'Twitter/X',
            'supports_playlist': False,
            'live_support': False
        },
        'kick': {
            'patterns': [r'kick\.com'],
            'name': 'Kick',
            'supports_playlist': False,
            'live_support': True,
            'special_handling': True
        },
        'twitch': {
            'patterns': [r'twitch\.tv', r'clips\.twitch\.tv'],
            'name': 'Twitch',
            'supports_playlist': False,
            'live_support': True
        },
        'vimeo': {
            'patterns': [r'vimeo\.com'],
            'name': 'Vimeo',
            'supports_playlist': False,
            'live_support': False
        },
        'dailymotion': {
            'patterns': [r'dailymotion\.com', r'dai\.ly'],
            'name': 'Dailymotion',
            'supports_playlist': False,
            'live_support': False
        },
        'soundcloud': {
            'patterns': [r'soundcloud\.com'],
            'name': 'SoundCloud',
            'supports_playlist': True,
            'live_support': False
        },
        'reddit': {
            'patterns': [r'reddit\.com', r'redd\.it'],
            'name': 'Reddit',
            'supports_playlist': False,
            'live_support': False
        }
    }
    
    @classmethod
    def detect(cls, url):
        """Detect platform from URL"""
        if not url:
            return None, {}
        
        url_lower = url.lower()
        for platform_id, info in cls.PLATFORMS.items():
            for pattern in info['patterns']:
                if re.search(pattern, url_lower):
                    return platform_id, info
        
        return 'generic', {'name': 'Generic URL', 'supports_playlist': False, 'live_support': False}
    
    @classmethod
    def is_playlist(cls, url):
        """Check if URL is a playlist"""
        url_lower = url.lower()
        playlist_indicators = ['playlist', '/sets/', '/album/', '/collection/']
        return any(indicator in url_lower for indicator in playlist_indicators)


class DownloadManager:
    """Manages downloads with proper threading and error handling"""
    
    def __init__(self, progress_callback=None, status_callback=None):
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.download_lock = Lock()
        self.stop_event = Event()
        self.current_process = None
        self.ydl_instance = None
        self.force_stop = False
        self.download_thread_id = None
        
    def stop_download(self):
        """Stop current download immediately"""
        self.force_stop = True
        self.stop_event.set()
        
        # Immediately terminate yt-dlp instance
        if self.ydl_instance:
            try:
                self.ydl_instance._download_retcode = 1
                # Force close the yt-dlp instance
                if hasattr(self.ydl_instance, 'close'):
                    self.ydl_instance.close()
            except:
                pass
        
        # Aggressively kill subprocess
        if self.current_process:
            try:
                # Try graceful termination first
                self.current_process.terminate()
                
                # If still running after 100ms, force kill
                try:
                    self.current_process.wait(timeout=0.1)
                except subprocess.TimeoutExpired:
                    self.current_process.kill()
                    
                # For Windows, also try to kill child processes
                if sys.platform == 'win32':
                    try:
                        parent = psutil.Process(self.current_process.pid)
                        for child in parent.children(recursive=True):
                            child.kill()
                        parent.kill()
                    except:
                        pass
            except:
                pass
    
    def reset(self):
        """Reset download state"""
        self.stop_event.clear()
        self.force_stop = False
        self.current_process = None
        self.ydl_instance = None
        self.download_thread_id = None
    
    def _progress_hook(self, d):
        """Progress hook for yt-dlp"""
        if self.stop_event.is_set() or self.force_stop:
            raise KeyboardInterrupt("Download stopped by user")
        
        if self.progress_callback and not self.force_stop:
            self.progress_callback(d)
    
    def download(self, url, output_path, download_type='video', quality='720p', audio_format='mp3'):
        """Main download method with platform-specific handling"""
        
        # Detect platform
        platform, platform_info = PlatformDetector.detect(url)
        
        # Handle Kick specially
        if platform == 'kick':
            return self._download_kick(url, output_path, quality)
        
        # Use yt-dlp for all other platforms
        return self._download_with_ytdlp(url, output_path, download_type, quality, audio_format, platform_info)
    
    def _download_kick(self, url, output_path, quality='best'):
        """Special handling for Kick.com using yt-dlp with custom options"""
        try:
            if self.status_callback:
                self.status_callback("Preparing Kick download...")
            
            # Create output directory
            os.makedirs(output_path, exist_ok=True)
            
            # Extract username/channel from URL
            username = "kick_stream"
            match = re.search(r'kick\.com/([^/?]+)', url)
            if match:
                username = match.group(1)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Configure yt-dlp for Kick
            ydl_opts = {
                'outtmpl': os.path.join(output_path, f'kick_{username}_{timestamp}.%(ext)s'),
                'progress_hooks': [self._progress_hook],
                'quiet': False,  # Show verbose output for debugging
                'verbose': True,
                'no_warnings': False,
                
                # Network options
                'socket_timeout': 60,
                'retries': 10,
                'fragment_retries': 10,
                'skip_unavailable_fragments': True,
                
                # Format selection - Kick specific
                'format': 'best[height<=1080]/best',  # Limit to 1080p max for stability
                
                # Live stream options
                'live_from_start': False,  # Don't try to download from start of stream
                'wait_for_video': 10,  # Wait up to 10 seconds for video to be available
                
                # Cookies and headers to bypass restrictions
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Sec-Fetch-Mode': 'navigate',
                },
                
                # Use external downloader for better performance with live streams
                'external_downloader': 'ffmpeg',
                'external_downloader_args': ['-reconnect', '1', '-reconnect_streamed', '1', '-reconnect_delay_max', '5'],
                
                # Don't check certificates (sometimes helps with CDN issues)
                'nocheckcertificate': True,
                
                # Continue partial downloads
                'continuedl': True,
            }
            
            # Check if it's a VOD or live stream
            if '/video/' in url or '/clip/' in url:
                if self.status_callback:
                    self.status_callback("Downloading Kick VOD/Clip...")
                ydl_opts['live_from_start'] = False
            else:
                if self.status_callback:
                    self.status_callback("Downloading Kick live stream (this may take time)...")
                ydl_opts['live_from_start'] = False
                
                # For live streams, download for a specific duration (optional)
                # ydl_opts['match_filter'] = 'duration < 3600'  # Limit to 1 hour
            
            # Try to download with yt-dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.ydl_instance = ydl
                
                try:
                    # Extract info first to check availability
                    if self.status_callback:
                        self.status_callback("Extracting video information from Kick...")
                    
                    info = ydl.extract_info(url, download=False)
                    
                    if not info:
                        return False, "Could not extract video information from Kick"
                    
                    # Check if live
                    is_live = info.get('is_live', False)
                    title = info.get('title', 'Unknown')
                    
                    if is_live:
                        if self.status_callback:
                            self.status_callback(f"Downloading live stream: {title}")
                    else:
                        if self.status_callback:
                            self.status_callback(f"Downloading VOD: {title}")
                    
                    # Download the video
                    ydl.download([url])
                    
                    self.ydl_instance = None
                    return True, f"Successfully downloaded from Kick: {title}"
                    
                except yt_dlp.utils.DownloadError as e:
                    error_msg = str(e)
                    
                    # Parse specific Kick errors
                    if "403" in error_msg or "Forbidden" in error_msg:
                        return False, "Kick stream is private or requires authentication"
                    elif "404" in error_msg or "Not Found" in error_msg:
                        return False, "Kick stream not found or has ended"
                    elif "is_live" in error_msg:
                        return False, "Live stream has ended or is not available"
                    else:
                        return False, f"Kick download error: {error_msg[:200]}"
                        
        except KeyboardInterrupt:
            return False, "Download stopped by user"
        except Exception as e:
            return False, f"Kick download failed: {str(e)[:200]}"
        finally:
            self.ydl_instance = None
    
    def _download_with_ytdlp(self, url, output_path, download_type, quality, audio_format, platform_info):
        """Download using yt-dlp for most platforms"""
        try:
            os.makedirs(output_path, exist_ok=True)
            
            # Base configuration
            ydl_opts = {
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self._progress_hook],
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': False,
                'continuedl': True,
                'noprogress': False,
                
                # Network settings
                'socket_timeout': 30,
                'retries': 10,
                'fragment_retries': 10,
                'skip_unavailable_fragments': False,
                
                # File naming
                'restrictfilenames': True,
                'windowsfilenames': True,
                
                # Headers for bypassing restrictions
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept-Language': 'en-US,en;q=0.5',
                },
                
                'nocheckcertificate': True,
            }
            
            # Configure format based on download type
            if download_type == 'audio':
                ydl_opts['format'] = 'bestaudio/best'
                
                if audio_format != 'best':
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': audio_format,
                        'preferredquality': '320',  # High quality audio
                    }]
                    
                    # Add metadata for music
                    ydl_opts['postprocessors'].append({
                        'key': 'FFmpegMetadata',
                        'add_metadata': True,
                    })
                    
                    # Embed thumbnail for music files
                    if audio_format in ['mp3', 'm4a']:
                        ydl_opts['writethumbnail'] = True
                        ydl_opts['postprocessors'].append({
                            'key': 'EmbedThumbnail',
                        })
            else:
                # Video format selection
                if quality == 'highest':
                    ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                else:
                    try:
                        height = int(quality.replace('p', ''))
                        ydl_opts['format'] = f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={height}]/best'
                    except:
                        ydl_opts['format'] = 'best'
                
                # Merge output to mp4
                ydl_opts['merge_output_format'] = 'mp4'
            
            # Platform-specific configurations
            if 'instagram' in platform_info.get('name', '').lower():
                # Instagram often requires cookies
                ydl_opts['cookiesfrombrowser'] = 'chrome'
                
            elif 'tiktok' in platform_info.get('name', '').lower():
                # TikTok specific options
                ydl_opts['format'] = 'best'
                
            elif 'twitter' in platform_info.get('name', '').lower():
                # Twitter/X specific
                ydl_opts['format'] = 'best[protocol^=http]'
                
            elif 'facebook' in platform_info.get('name', '').lower():
                # Facebook often needs cookies
                ydl_opts['cookiesfrombrowser'] = 'chrome'
            
            # Download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.ydl_instance = ydl
                
                if self.status_callback:
                    self.status_callback(f"Downloading from {platform_info.get('name', 'Unknown')}...")
                
                # Extract and download
                info = ydl.extract_info(url, download=True)
                
                # Get actual filename
                filename = ydl.prepare_filename(info)
                if download_type == 'audio' and audio_format != 'best':
                    filename = os.path.splitext(filename)[0] + f'.{audio_format}'
                
                title = info.get('title', 'Unknown')
                self.ydl_instance = None
                
                return True, f"Successfully downloaded: {title}"
                
        except KeyboardInterrupt:
            return False, "Download stopped by user"
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if "private" in error_msg.lower():
                return False, "Content is private or requires login"
            elif "404" in error_msg or "not found" in error_msg.lower():
                return False, "Content not found or has been removed"
            else:
                return False, f"Download failed: {error_msg[:200]}"
        except Exception as e:
            return False, f"Error: {str(e)[:200]}"
        finally:
            self.ydl_instance = None


class YouTubeDownloader:
    """Main application class with improved architecture"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Video Downloader Pro 2.0")
        self.root.geometry('900x700')
        self.root.minsize(700, 500)
        
        # Application state
        self.config_file = Path.home() / ".video_downloader_config.json"
        self.download_manager = DownloadManager(
            progress_callback=self.on_progress,
            status_callback=self.on_status_update
        )
        self.download_thread = None
        self.downloading = False
        self.download_queue = queue.Queue()
        self.stop_requested = False
        self.ui_update_queue = queue.Queue()
        
        # Smooth progress bar variables
        self.current_progress = 0.0
        self.target_progress = 0.0
        self.progress_animation_id = None
        self.smooth_progress_enabled = True
        
        # UI Variables
        self.url = tk.StringVar()
        self.download_path = tk.StringVar()
        self.download_type = tk.StringVar(value='video')
        self.video_quality = tk.StringVar(value='720p')
        self.audio_format = tk.StringVar(value='mp3')
        self.status_text = tk.StringVar(value="Ready")
        self.platform_text = tk.StringVar(value="")
        
        # Initialize
        self.load_config()
        self.setup_ui()
        self.start_clipboard_monitor()
        self.start_ui_update_processor()
        
        # Start smooth progress bar demo
        self._demo_smooth_progress()
        
        # Window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Create the user interface"""
        
        # Configure styles with smooth progress bar
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Segoe UI', 14, 'bold'))
        style.configure('Platform.TLabel', font=('Segoe UI', 10), foreground='#0066cc')
        style.configure('Status.TLabel', font=('Segoe UI', 9))
        
        # Configure smooth progress bar style
        style.configure('Smooth.Horizontal.TProgressbar', 
                       background='#4CAF50',  # Green color
                       troughcolor='#E0E0E0',  # Light gray trough
                       borderwidth=0,
                       lightcolor='#4CAF50',
                       darkcolor='#4CAF50')
        
        # Alternative smooth style for different themes
        style.configure('Smooth.TProgressbar',
                       background='#2196F3',  # Blue color
                       troughcolor='#F5F5F5',
                       borderwidth=0)
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Universal Video Downloader Pro", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # URL Input Section
        url_frame = ttk.LabelFrame(main_frame, text="Video/Audio URL", padding=10)
        url_frame.pack(fill=tk.X, pady=5)
        
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url, font=('Segoe UI', 10))
        self.url_entry.pack(fill=tk.X, pady=5)
        self.url_entry.bind('<KeyRelease>', self.on_url_change)
        
        # Platform indicator
        self.platform_label = ttk.Label(url_frame, textvariable=self.platform_text, style='Platform.TLabel')
        self.platform_label.pack(anchor='w')
        
        # Setup drag-and-drop if available
        if HAS_DND:
            self.setup_drag_drop()
        
        # Download Options
        options_frame = ttk.LabelFrame(main_frame, text="Download Options", padding=10)
        options_frame.pack(fill=tk.X, pady=10)
        
        # Type selection
        type_row = ttk.Frame(options_frame)
        type_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(type_row, text="Type:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(type_row, text="Video", variable=self.download_type, 
                       value='video', command=self.update_format_options).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_row, text="Audio Only", variable=self.download_type, 
                       value='audio', command=self.update_format_options).pack(side=tk.LEFT, padx=5)
        
        # Quality/Format selection
        self.format_frame = ttk.Frame(options_frame)
        self.format_frame.pack(fill=tk.X, pady=5)
        
        self.quality_label = ttk.Label(self.format_frame, text="Quality:")
        self.quality_combo = ttk.Combobox(self.format_frame, textvariable=self.video_quality,
                                         values=['highest', '2160p', '1440p', '1080p', '720p', '480p', '360p'],
                                         state='readonly', width=12)
        
        self.format_label = ttk.Label(self.format_frame, text="Format:")
        self.format_combo = ttk.Combobox(self.format_frame, textvariable=self.audio_format,
                                        values=['mp3', 'm4a', 'opus', 'flac', 'best'],
                                        state='readonly', width=12)
        
        self.update_format_options()
        
        # Download Location
        location_frame = ttk.LabelFrame(main_frame, text="Download Location", padding=10)
        location_frame.pack(fill=tk.X, pady=5)
        
        loc_row = ttk.Frame(location_frame)
        loc_row.pack(fill=tk.X)
        
        ttk.Entry(loc_row, textvariable=self.download_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(loc_row, text="Browse...", command=self.browse_folder).pack(side=tk.RIGHT)
        
        # Progress Section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding=10)
        progress_frame.pack(fill=tk.X, pady=10)
        
        # Create ultra-smooth progress bar
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                          mode='determinate',
                                          style='Smooth.Horizontal.TProgressbar',
                                          length=400,
                                          maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Set initial value for smooth start
        self.progress_bar['value'] = 0
        
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_text, style='Status.TLabel')
        self.status_label.pack(fill=tk.X)
        
        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=15)
        
        self.download_btn = ttk.Button(button_frame, text="⬇ Download", 
                                      command=self.start_download, width=20)
        self.download_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="⏹ Stop", 
                                  command=self.stop_download, width=15, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(button_frame, text="Clear", 
                                   command=self.clear_fields, width=15)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Supported platforms info
        info_text = "Supports: YouTube, Instagram, Facebook, TikTok, Twitter/X, Kick, Twitch, and more!"
        ttk.Label(main_frame, text=info_text, font=('Segoe UI', 8), foreground='gray').pack(pady=5)
    
    def update_format_options(self):
        """Update quality/format options based on selected type"""
        for widget in self.format_frame.winfo_children():
            widget.pack_forget()
        
        if self.download_type.get() == 'video':
            self.quality_label.pack(side=tk.LEFT, padx=(0, 5))
            self.quality_combo.pack(side=tk.LEFT)
        else:
            self.format_label.pack(side=tk.LEFT, padx=(0, 5))
            self.format_combo.pack(side=tk.LEFT)
    
    def on_url_change(self, event=None):
        """Handle URL input change"""
        url = self.url.get().strip()
        if not url:
            self.platform_text.set("")
            return
        
        platform, info = PlatformDetector.detect(url)
        platform_name = info.get('name', 'Unknown')
        
        # Check for playlist
        if PlatformDetector.is_playlist(url):
            self.platform_text.set(f"✓ {platform_name} Playlist detected")
        else:
            self.platform_text.set(f"✓ {platform_name} detected")
        
        # Auto-switch to audio for music platforms
        if platform in ['youtube_music', 'soundcloud']:
            self.download_type.set('audio')
            self.update_format_options()
    
    def browse_folder(self):
        """Open folder selection dialog"""
        folder = filedialog.askdirectory()
        if folder:
            self.download_path.set(folder)
            self.save_config()
    
    def clear_fields(self):
        """Clear all input fields with smooth progress reset"""
        self.url.set("")
        self.platform_text.set("")
        
        # Smooth progress bar reset
        self.current_progress = 0.0
        self.target_progress = 0.0
        self.progress_bar['value'] = 0
        
        # Cancel any running animation
        if self.progress_animation_id:
            self.root.after_cancel(self.progress_animation_id)
            self.progress_animation_id = None
        
        self.status_text.set("Ready")
    
    def on_progress(self, d):
        """Handle download progress updates - optimized for speed"""
        if self.stop_requested or self.download_manager.force_stop:
            return
            
        if d['status'] == 'downloading':
            if 'total_bytes' in d or 'total_bytes_estimate' in d:
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                
                if total > 0:
                    percentage = (downloaded / total) * 100
                    # Use queue for faster UI updates
                    self.ui_update_queue.put(('progress', percentage, downloaded, total))
                    
        elif d['status'] == 'finished':
            self.ui_update_queue.put(('status', "Processing..."))
    
    def _update_progress(self, percentage, downloaded, total):
        """Update progress bar and status (UI thread) - ULTRA SMOOTH"""
        if not self.stop_requested:
            # Set target for smooth animation
            self.target_progress = percentage
            
            # Start smooth animation if not already running
            if self.smooth_progress_enabled and self.progress_animation_id is None:
                self._animate_progress()
            
            # Update status text immediately
            size_str = f"{self._format_size(downloaded)}/{self._format_size(total)}"
            self.status_text.set(f"Downloading... {int(percentage)}% ({size_str})")
            
            # Force immediate UI update
            self.root.update_idletasks()
    
    def on_status_update(self, message):
        """Handle status message updates - optimized"""
        if not self.stop_requested:
            self.ui_update_queue.put(('status', message))
    
    def _format_size(self, bytes_val):
        """Format bytes to human readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} TB"
    
    def start_download(self):
        """Start download process - optimized for immediate response"""
        
        # Validate inputs
        url = self.url.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url.set(url)
        
        path = self.download_path.get()
        if not path:
            messagebox.showerror("Error", "Please select download location")
            return
        
        # IMMEDIATE UI updates for instant feedback
        self.downloading = True
        self.stop_requested = False
        self.download_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.clear_btn.config(state=tk.DISABLED)
        
        # Reset progress bar smoothly
        self.current_progress = 0.0
        self.target_progress = 0.0
        self.progress_bar['value'] = 0
        
        # Cancel any running animation
        if self.progress_animation_id:
            self.root.after_cancel(self.progress_animation_id)
            self.progress_animation_id = None
        
        self.status_text.set("Starting download...")
        
        # Force immediate UI update
        self.root.update_idletasks()
        
        # Reset download manager
        self.download_manager.reset()
        
        # Start download in thread with immediate feedback
        self.download_thread = Thread(target=self._download_worker, args=(url, path), daemon=True)
        self.download_manager.download_thread_id = self.download_thread.ident
        self.download_thread.start()
        
        # Immediate status update
        self.status_text.set("Download starting...")
        self.root.update_idletasks()
    
    def _download_worker(self, url, path):
        """Worker thread for downloading"""
        try:
            # Get download parameters
            download_type = self.download_type.get()
            quality = self.video_quality.get() if download_type == 'video' else None
            audio_format = self.audio_format.get() if download_type == 'audio' else None
            
            # Perform download
            success, message = self.download_manager.download(
                url, path, download_type, quality, audio_format
            )
            
            # Update UI with result
            self.root.after(0, self._download_complete, success, message)
            
        except Exception as e:
            self.root.after(0, self._download_complete, False, f"Unexpected error: {str(e)[:200]}")
        finally:
            self.downloading = False
    
    def _download_complete(self, success, message):
        """Handle download completion (UI thread) - optimized with smooth finish"""
        self.downloading = False
        self.stop_requested = False
        
        # Update UI state immediately
        self.download_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.clear_btn.config(state=tk.NORMAL)
        
        if success:
            # Smooth progress to 100%
            self.target_progress = 100.0
            if self.smooth_progress_enabled:
                self._animate_progress()
            else:
                self.progress_bar['value'] = 100
            
            self.status_text.set(f"✓ {message}")
            # Show success message without blocking
            self.root.after(100, lambda: messagebox.showinfo("Success", message))
        else:
            # Smooth progress reset to 0%
            self.target_progress = 0.0
            if self.smooth_progress_enabled:
                self._animate_progress()
            else:
                self.progress_bar['value'] = 0
            
            self.status_text.set(f"✗ Failed: {message[:100]}")
            if not "stopped by user" in message.lower():
                # Show error message without blocking
                self.root.after(100, lambda: messagebox.showerror("Download Failed", message))
        
        # Force immediate UI update
        self.root.update_idletasks()
    
    def stop_download(self):
        """Stop current download - IMMEDIATE response"""
        if not self.downloading:
            return
        
        # IMMEDIATE UI feedback
        self.stop_requested = True
        self.status_text.set("Stopping...")
        self.root.update_idletasks()
        
        # Aggressive stop
        self.download_manager.stop_download()
        
        # Immediate UI reset
        self._reset_ui_immediately()
        
        # Check if thread is still alive and force kill if needed
        if self.download_thread and self.download_thread.is_alive():
            # Give it 100ms to stop gracefully, then force kill
            self.root.after(100, self._force_stop_thread)
        else:
            self._finalize_stop()
    
    def _reset_ui_immediately(self):
        """Reset UI immediately when stop is pressed"""
        self.downloading = False
        self.download_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.clear_btn.config(state=tk.NORMAL)
        
        # Reset progress bar smoothly
        self.current_progress = 0.0
        self.target_progress = 0.0
        self.progress_bar['value'] = 0
        
        # Cancel any running animation
        if self.progress_animation_id:
            self.root.after_cancel(self.progress_animation_id)
            self.progress_animation_id = None
        
        self.status_text.set("Stopped")
        self.root.update_idletasks()
    
    def _force_stop_thread(self):
        """Force stop the download thread if still running"""
        if self.download_thread and self.download_thread.is_alive():
            # Try to interrupt the thread
            try:
                if hasattr(self.download_thread, '_stop'):
                    self.download_thread._stop()
            except:
                pass
        self._finalize_stop()
    
    def _finalize_stop(self):
        """Finalize the stop process"""
        self.downloading = False
        self.stop_requested = False
        self.status_text.set("Download stopped")
        self.root.update_idletasks()
    
    def setup_drag_drop(self):
        """Setup drag and drop for URL entry"""
        try:
            self.url_entry.drop_target_register(DND_FILES)
            self.url_entry.dnd_bind('<<Drop>>', self.on_drop)
        except:
            pass
    
    def on_drop(self, event):
        """Handle dropped URLs"""
        try:
            data = event.data.strip()
            if data.startswith('{') and data.endswith('}'):
                data = data[1:-1]
            
            # Check for URL
            if data.startswith(('http://', 'https://', 'www.')):
                self.url.set(data)
                self.on_url_change()
        except:
            pass
    
    def start_clipboard_monitor(self):
        """Monitor clipboard for URLs"""
        self._last_clipboard = ""
        self._check_clipboard()
    
    def _check_clipboard(self):
        """Check clipboard for new URLs"""
        try:
            current = self.root.clipboard_get().strip()
            
            # Check if new content is a URL
            if current != self._last_clipboard and not self.downloading:
                if current.startswith(('http://', 'https://')) and any(
                    domain in current.lower() for domain in [
                        'youtube.', 'instagram.', 'tiktok.', 'facebook.', 
                        'twitter.', 'x.com', 'kick.', 'twitch.', 'vimeo.', 
                        'dailymotion.', 'soundcloud.', 'reddit.'
                    ]
                ):
                    self.url.set(current)
                    self.on_url_change()
                    self.status_text.set("✓ URL detected from clipboard")
                
                self._last_clipboard = current
        except:
            pass
        
        # Check every 500ms
        self.root.after(500, self._check_clipboard)
    
    def start_ui_update_processor(self):
        """Start the UI update processor for smooth updates"""
        self._process_ui_updates()
    
    def _process_ui_updates(self):
        """Process UI updates from queue - runs every 8ms for 120fps ultra-smooth"""
        try:
            while not self.ui_update_queue.empty():
                update = self.ui_update_queue.get_nowait()
                if update[0] == 'progress':
                    self._update_progress(update[1], update[2], update[3])
                elif update[0] == 'status':
                    self.status_text.set(update[1])
        except queue.Empty:
            pass
        
        # Schedule next update (120fps for ultra-smooth)
        self.root.after(8, self._process_ui_updates)
    
    def _demo_smooth_progress(self):
        """Demo smooth progress bar animation on startup"""
        if not self.downloading:
            # Animate progress bar from 0 to 100 and back to 0
            self.target_progress = 100.0
            self.root.after(2000, lambda: setattr(self, 'target_progress', 0.0))
            self.root.after(4000, lambda: setattr(self, 'target_progress', 0.0))
            
            # Start smooth animation
            if self.smooth_progress_enabled:
                self._animate_progress()
    
    def _animate_progress(self):
        """Animate progress bar smoothly to target value with advanced easing"""
        if self.stop_requested or not self.smooth_progress_enabled:
            self.progress_animation_id = None
            return
        
        # Calculate smooth interpolation with advanced easing
        diff = self.target_progress - self.current_progress
        
        if abs(diff) < 0.05:  # Ultra-precise threshold
            self.current_progress = self.target_progress
            self.progress_bar['value'] = self.current_progress
            self.progress_animation_id = None
        else:
            # Advanced easing function for ultra-smooth animation
            # Uses ease-out cubic for natural deceleration
            progress_ratio = abs(diff) / 100.0  # Normalize to 0-1
            
            # Dynamic easing factor based on distance (closer = slower for precision)
            if progress_ratio > 0.5:
                ease_factor = 0.25  # Fast for large jumps
            elif progress_ratio > 0.1:
                ease_factor = 0.15  # Medium for medium jumps
            else:
                ease_factor = 0.08  # Slow for fine adjustments
            
            # Apply easing with cubic interpolation
            self.current_progress += diff * ease_factor
            
            # Ensure we don't overshoot
            if (diff > 0 and self.current_progress > self.target_progress) or \
               (diff < 0 and self.current_progress < self.target_progress):
                self.current_progress = self.target_progress
            
            self.progress_bar['value'] = self.current_progress
            
            # Continue animation at 120fps for ultra-smooth
            self.progress_animation_id = self.root.after(8, self._animate_progress)
    
    def load_config(self):
        """Load saved configuration"""
        default_config = {
            'download_path': str(Path.home() / 'Downloads'),
            'download_type': 'video',
            'video_quality': '720p',
            'audio_format': 'mp3'
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                self.download_path.set(config.get('download_path', default_config['download_path']))
                self.download_type.set(config.get('download_type', default_config['download_type']))
                self.video_quality.set(config.get('video_quality', default_config['video_quality']))
                self.audio_format.set(config.get('audio_format', default_config['audio_format']))
            else:
                # Set defaults
                for key, value in default_config.items():
                    getattr(self, key).set(value)
        except:
            # Use defaults on error
            for key, value in default_config.items():
                getattr(self, key).set(value)
    
    def save_config(self):
        """Save current configuration"""
        try:
            config = {
                'download_path': self.download_path.get(),
                'download_type': self.download_type.get(),
                'video_quality': self.video_quality.get(),
                'audio_format': self.audio_format.get()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except:
            pass
    
    def on_closing(self):
        """Handle window close event - optimized"""
        # Stop any active downloads immediately
        if self.downloading:
            self.stop_requested = True
            self.download_manager.stop_download()
            # Don't wait, just force close
            
        # Save configuration
        self.save_config()
        
        # Destroy window
        self.root.destroy()


def check_dependencies():
    """Check and install required dependencies"""
    required = {
        'yt-dlp': 'yt-dlp',
        'tkinterdnd2': 'tkinterdnd2'  # Optional
    }
    
    for module, package in required.items():
        try:
            __import__(module.replace('-', '_'))
        except ImportError:
            print(f"Installing {package}...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-U', package])
            except:
                if module != 'tkinterdnd2':  # Only yt-dlp is critical
                    print(f"Failed to install {package}. Please install manually: pip install {package}")
                    sys.exit(1)


def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL,
                      creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
        return True
    except:
        return False


def main():
    """Main entry point"""
    
    # Check dependencies
    print("Checking dependencies...")
    check_dependencies()
    
    # Check FFmpeg
    if not check_ffmpeg():
        print("\n" + "="*60)
        print("WARNING: FFmpeg not found!")
        print("FFmpeg is required for video/audio conversion.")
        print("Download from: https://ffmpeg.org/download.html")
        print("="*60 + "\n")
    
    # Create main window
    if HAS_DND:
        try:
            root = TkinterDnD.Tk()
        except:
            root = tk.Tk()
    else:
        root = tk.Tk()
    
    # Set window properties
    root.resizable(True, True)
    
    # Try to set window icon
    try:
        if sys.platform == 'win32':
            root.iconbitmap(default='icon.ico')
    except:
        pass
    
    # Create and run application
    app = YouTubeDownloader(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Start main loop
    root.mainloop()


if __name__ == "__main__":
    main()