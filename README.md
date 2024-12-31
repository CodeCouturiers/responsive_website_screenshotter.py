# Responsive Website Screenshotter

A Python tool for automatically capturing website screenshots across multiple device viewports and creating a visual collage. This tool supports 20 different viewport sizes covering modern desktop resolutions, Apple devices, Android tablets, and popular smartphones from 2024.

## Features

- Captures screenshots for 20 different device viewports
- Supports modern resolutions including 4K displays
- Creates a organized collage of all screenshots
- Handles retries for failed captures
- Supports concurrent screenshot capture
- Includes detailed logging
- Optimized for performance and reliability

## Requirements

- Python 3.7+
- Chrome/Chromium browser
- ChromeDriver (compatible with your Chrome version)

## Dependencies

```bash
pip install selenium Pillow
```

## Supported Devices

### Desktop
- Full HD (1920x1080)
- 2K QHD (2560x1440)
- 4K UHD (3840x2160)
- Common Laptop (1366x768)
- HD+ Laptop (1536x864)

### Apple Devices
- MacBook Pro 15" (2880x1800)
- MacBook Pro 13" (2560x1600)
- iPad Pro 12.9" (2732x2048)
- iPad Pro 11" (2388x1668)
- iPad Air/10.9" (2048x1536)

### Android Tablets
- Samsung Tab S9 (2560x1600)
- Lenovo Tab P12 (2000x1200)
- Xiaomi Pad 6 (2160x1620)

### Smartphones
- iPhone 15 Pro Max (1290x2796)
- iPhone 15 Pro (1179x2556)
- iPhone 15 (1170x2532)
- Samsung S24 Ultra (1440x3088)
- Samsung S24 (1080x2340)
- Google Pixel 8 Pro (1080x2400)
- OnePlus 12 (1080x2400)

## Usage

1. Clone the repository
2. Install dependencies
3. Update the `OUTPUT_DIR` and `URL` variables in the script
4. Run the script:

```bash
python responsive_website_screenshotter.py
```

## Configuration

You can modify the following parameters in the script:

- `OUTPUT_DIR`: Directory where screenshots and collage will be saved
- `URL`: Target website URL
- `MAX_WORKERS`: Number of concurrent screenshot operations (default: 3)
- `retry_count`: Number of retry attempts for failed screenshots (default: 3)

## Output

The script generates:
- Individual screenshots for each viewport
- A combined collage image showing all successful captures
- Detailed logging of the capture process

## Error Handling

- Automatic retry for failed captures
- Detailed error logging
- Graceful handling of timeout and connection issues
- Recovery from partial failures

## Performance Tips

1. Adjust `MAX_WORKERS` based on your system's capabilities
2. Increase timeout values for slower websites
3. Modify wait times for dynamic content if needed
4. Use SSD storage for faster image processing

## Known Limitations

- May have issues with websites that block headless browsers
- Some very dynamic websites might require additional wait times
- High-resolution captures may require significant memory

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

MIT License
