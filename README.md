# pin_scraper

# Pinterest Board Image Downloader for macOS

A Python script that automatically downloads all images from a Pinterest board using your existing Chrome browser session. This tool is specifically optimized for macOS and uses your logged-in Pinterest account to access boards.

## Features

- 🔐 **Uses Your Chrome Profile**: Leverages your existing Chrome sessions and cookies
- 🖼️ **High-Resolution Images**: Automatically fetches higher quality versions of images
- 📜 **Smart Scrolling**: Automatically scrolls to load all images on the board
- 🔄 **Duplicate Prevention**: Uses URL hashing to avoid downloading the same image twice
- 🎯 **Login Detection**: Checks if you're properly logged into Pinterest
- 📊 **Progress Tracking**: Real-time progress updates during download

## Prerequisites

### macOS Requirements
- macOS with Google Chrome installed
- Python 3.6 or higher
- ChromeDriver

### Install ChromeDriver
```bash
# Using Homebrew (recommended)
brew install chromedriver

# Or download manually from:
# https://chromedriver.chromium.org/
```

### Python Dependencies
```bash
pip install selenium pillow requests
```

## Installation

1. **Clone or download the script**
   ```bash
   # Save the script as pinterest_downloader.py
   ```

2. **Make the script executable**
   ```bash
   chmod +x pinterest_downloader.py
   ```

3. **Update the username (if needed)**
   - Open the script in a text editor
   - Find line: `username = os.getenv('USER')`
   - Replace `os.getenv('USER')` with your macOS username

4. **Update URL check (if needed)**
   - If the board you planning to download starts from any othe prefix than `https://jp.`
   - Find line: `if not board_url.startswith('https://jp.pinterest.com/'):`
   - Replace `https://jp.` with prefix you planning to use

## Usage

### Basic Command
```bash
python pinterest_downloader.py "PINTEREST_BOARD_URL" "OUTPUT_FOLDER"
```

### Example
```bash
python pinterest_downloader.py "https://jp.pinterest.com/user/my-board/" "./downloaded_images"
```

### Parameters
- `PINTEREST_BOARD_URL`: Full URL to the Pinterest board you want to download
- `OUTPUT_FOLDER`: Local directory where images will be saved

## How It Works

1. **Browser Setup**: Opens Chrome using your existing user profile
2. **Login Verification**: Checks if you're logged into Pinterest
3. **Board Access**: Navigates to the specified Pinterest board
4. **Content Loading**: Automatically scrolls to load all images
5. **Image Extraction**: Finds and extracts high-resolution image URLs
6. **Batch Download**: Downloads all images to the specified folder

## File Naming Convention

Downloaded images are named using the format:
```
pinterest_0001_a1b2c3d4.jpg
```
- Sequential numbering (`0001`, `0002`, etc.)
- URL hash to ensure uniqueness
- `.jpg` extension

## Important Notes

### Before Running
- ✅ Ensure you're logged into Pinterest in Chrome
- ✅ Close all Chrome windows before running the script
- ✅ Verify ChromeDriver is installed and accessible
- ✅ Check that the board URL is accessible

### URL Requirements
- Must start with `https://ru.pinterest.com/`
- Must be a public board or one you have access to
- Should be a board URL, not a pin URL

### Performance
- The script includes delays to be respectful to Pinterest's servers
- Download speed depends on your internet connection and board size
- Large boards may take several minutes to process

## Troubleshooting

### Common Issues

1. **"ChromeDriver not found"**
   ```bash
   brew install chromedriver
   ```

2. **Login redirects**
   - Make sure Chrome is closed before running
   - Verify you're logged into Pinterest in your regular Chrome

3. **No images found**
   - Check the board URL is correct
   - Ensure the board is public or you have access
   - Try running with `headless=False` to see what's happening

4. **Permission errors**
   ```bash
   chmod +x pinterest_downloader.py
   ```

### Manual Login
If the script detects you're not logged in:
1. It will pause and display a message
2. A Chrome window will open
3. Log in to Pinterest manually
4. Press Enter in the terminal to continue
5. The script will continue find and process images after login

## Legal Considerations

- Respect Pinterest's Terms of Service
- Only download content you have permission to use
- Be mindful of copyright and intellectual property rights
- Use responsibly and consider rate limiting

## Support

For issues or questions:
1. Check that all prerequisites are installed
2. Verify your Pinterest board URL is correct
3. Ensure you're logged into Pinterest in Chrome
4. Check that ChromeDriver is properly installed

## License

This tool is for educational and personal use. Please respect website terms of service and copyright laws.