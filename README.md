# 🤖 Universal Video Downloader Telegram Bot

A powerful Telegram bot that downloads videos and music from multiple platforms and sends them directly to users in Telegram!

## 🎯 Features

### 📱 **Multi-Platform Support**
- 📺 **YouTube** - Videos, music, playlists
- 📷 **Instagram** - Posts, stories, reels
- 🎵 **TikTok** - Videos, music
- 👥 **Facebook** - Videos, posts
- 🐦 **Twitter/X** - Videos, tweets
- 🥊 **Kick** - Live streams, VODs
- 🎮 **Twitch** - Clips, highlights
- 🎬 **Vimeo** - Videos
- 🎶 **SoundCloud** - Music, tracks
- 🔗 **Reddit** - Videos, clips

### 🎬 **Download Options**
- **Video Formats:** MP4 (360p to 4K)
- **Audio Formats:** MP3, M4A, Opus, FLAC
- **Quality Selection:** Choose your preferred quality
- **Smart Detection:** Automatic platform detection
- **File Size Optimization:** Automatic compression

### 🚀 **Bot Features**
- **Interactive Interface:** Easy-to-use buttons and menus
- **Progress Updates:** Real-time download status
- **Error Handling:** Clear error messages and recovery
- **Statistics:** Download stats and success rates
- **File Management:** Automatic cleanup of temporary files

## 🛠 Installation & Setup

### **Quick Start (Automated Setup)**

1. **Clone or download this folder**
2. **Run the setup script:**
   ```bash
   python setup_bot.py
   ```
3. **Follow the interactive setup**
4. **Start the bot:**
   ```bash
   python telegram_bot.py
   ```

### **Manual Setup**

1. **Install Python 3.8+**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Create a Telegram bot:**
   - Message @BotFather on Telegram
   - Send `/newbot`
   - Follow instructions to get your bot token
4. **Create `.env` file:**
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   BOT_USERNAME=your_bot_username
   ```
5. **Run the bot:**
   ```bash
   python telegram_bot.py
   ```

## 📋 Requirements

### **System Requirements**
- Python 3.8 or higher
- Internet connection
- FFmpeg (recommended for audio conversion)

### **Python Dependencies**
- `python-telegram-bot` - Telegram Bot API
- `yt-dlp` - Video/audio downloader
- `python-dotenv` - Environment variables

### **Optional Dependencies**
- `ffmpeg` - For audio conversion and processing

## 🎮 How to Use

### **For Users (Telegram)**
1. **Find your bot:** Search for your bot username on Telegram
2. **Start the bot:** Send `/start`
3. **Send a link:** Paste any video/music URL
4. **Choose format:** Select video or audio
5. **Select quality:** Choose your preferred quality
6. **Wait for download:** Bot will send the file when ready!

### **For Bot Owner (Server)**
1. **Start the bot:** Run `python telegram_bot.py`
2. **Keep it running:** Bot needs to stay online
3. **Monitor logs:** Check for errors or issues
4. **Update regularly:** Keep dependencies updated

## 🔧 Configuration

### **Environment Variables (.env file)**
```env
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here
BOT_USERNAME=your_bot_username

# Optional
TEMP_DIR=temp_downloads
MAX_FILE_SIZE=2147483648
```

### **Bot Commands**
- `/start` - Show welcome message and menu
- `/help` - Get help and usage instructions
- `/stats` - Show download statistics
- `/settings` - Show current settings

## 📊 Bot Statistics

The bot tracks:
- **Total Downloads:** Number of download attempts
- **Successful Downloads:** Successful completions
- **Failed Downloads:** Failed attempts
- **Success Rate:** Percentage of successful downloads

## 🚨 Important Notes

### **File Size Limits**
- **Videos:** Up to 2GB (Telegram limit)
- **Audio:** Up to 50MB (recommended)
- **Larger files:** Will show error message

### **Platform Limitations**
- Some platforms may require cookies
- Private/restricted content cannot be downloaded
- Live streams may have limitations
- Some platforms may block automated downloads

### **Server Requirements**
- Stable internet connection
- Sufficient disk space for temporary files
- Regular cleanup of temp files
- Keep bot running 24/7 for availability

## 🔒 Security & Privacy

### **Data Handling**
- Temporary files are automatically deleted
- No permanent storage of downloaded content
- User data is not stored or logged
- Bot only processes URLs sent by users

### **Rate Limiting**
- Built-in rate limiting to prevent abuse
- File size limits to prevent server overload
- Error handling for failed downloads

## 🛠 Troubleshooting

### **Common Issues**

#### **Bot not responding**
- Check if bot is running
- Verify bot token is correct
- Check internet connection
- Review error logs

#### **Download failures**
- Check if URL is valid and public
- Some platforms may block automated downloads
- Try different quality settings
- Check file size limits

#### **File too large errors**
- Try downloading audio instead of video
- Select lower quality
- Some videos are too large for Telegram

### **Error Messages**
- **"No valid URL found"** - Send a proper video/music link
- **"Unsupported platform"** - Use supported platforms only
- **"Download failed"** - Try again or contact support
- **"File too large"** - Try audio format or lower quality

## 📈 Performance Optimization

### **Server Optimization**
- Use SSD storage for faster I/O
- Sufficient RAM for processing
- Fast internet connection
- Regular system maintenance

### **Bot Optimization**
- Monitor memory usage
- Clean up temp files regularly
- Update dependencies
- Monitor download success rates

## 🔄 Updates & Maintenance

### **Regular Updates**
- Update `yt-dlp` for latest platform support
- Update `python-telegram-bot` for API changes
- Monitor for security updates
- Test with new platforms

### **Maintenance Tasks**
- Clean up temp files
- Monitor disk space
- Check error logs
- Update bot features

## 📞 Support

### **Getting Help**
1. Check this README for common issues
2. Review error logs for specific problems
3. Test with different URLs and platforms
4. Contact support for persistent issues

### **Reporting Issues**
- Include error messages
- Provide example URLs that fail
- Share relevant log entries
- Describe steps to reproduce

## 🎉 Success Stories

Users love this bot because:
- ✅ **Easy to use** - Just send a link!
- ✅ **Fast downloads** - Optimized for speed
- ✅ **Multiple platforms** - Works with popular sites
- ✅ **Quality options** - Choose your preferred quality
- ✅ **Reliable** - Handles errors gracefully
- ✅ **Free to use** - No subscription required

## 🚀 Advanced Features

### **Customization Options**
- Modify supported platforms
- Adjust file size limits
- Custom quality options
- Add new download formats

### **Integration Possibilities**
- Web dashboard for statistics
- User management system
- Payment integration
- Advanced analytics

---

## 🎯 Ready to Deploy!

Your Telegram Video Downloader Bot is ready to serve users worldwide! 

**Key Benefits:**
- 🌍 **Global Access** - Works anywhere with internet
- 📱 **Mobile Friendly** - Perfect for mobile users
- 🎬 **Multi-Platform** - Supports all major platforms
- ⚡ **Fast & Reliable** - Optimized for performance
- 🔒 **Secure** - No data storage or privacy issues

**Start your bot and let users download videos with just a link!** 🚀