# Ventoy Image Writer

A modern PySide6 application for writing ISO images to USB devices using Ventoy. Features a clean, fluent design interface with support for multiple ISO files and automated Ventoy installation.

## Features

- **Modern UI**: Clean, fluent design interface with smooth animations
- **Multi-ISO Support**: Select and write multiple ISO files to a single USB device
- **Automated Ventoy Installation**: Automatically downloads and installs Ventoy v1.1.05
- **Smart Device Detection**: Automatically detects USB devices and Ventoy partitions
- **Progress Tracking**: Real-time progress updates and detailed logging
- **Secure Operations**: Uses pkexec for elevated privileges when needed
- **CSD Support**: Modern window decorations and styling

## Requirements

- Python 3.9 or higher
- PySide6 >= 6.5.0
- Linux with systemd and pkexec support
- USB device for installation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ventoy-image-writer.git
cd ventoy-image-writer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On fish: source venv/bin/activate.fish
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

## Building

To build a standalone executable:

```bash
source venv/bin/activate
pyinstaller --onefile --windowed main.py
```

The binary will be created in `dist/main`. You can copy it to your local bin directory:

```bash
cp dist/main ~/.local/share/bin/ventoy-image-writer
chmod +x ~/.local/share/bin/ventoy-image-writer
```

## Usage

1. **Select Images**: Click "Select Images" to choose one or more ISO files
2. **Choose Device**: Select a USB device from the dropdown menu
3. **Install Ventoy** (if needed): Click "Install Ventoy" to download and install Ventoy on the device
4. **Write Images**: Click "Write Images" to copy the ISO files to the Ventoy partition

### Features in Detail

- **Ventoy Detection**: The application automatically detects if a USB device already has Ventoy installed
- **Smart Installation**: If Ventoy is not found, the application will offer to install it automatically
- **Progress Monitoring**: Real-time progress updates and detailed logging for all operations
- **Multi-ISO Support**: Copy multiple ISO files to a single Ventoy USB device
- **Safe Operations**: All disk operations use pkexec for secure privilege escalation

## Project Structure

```
ventoy-image-writer/
├── main.py              # Application entry point
├── image_writer.py      # Main window and application logic
├── widgets/             # UI widgets
│   ├── modern_button.py    # Modern styled buttons
│   ├── device_selector.py  # USB device selection widget
│   └── progress_widget.py  # Progress tracking widget
├── helper/              # Helper modules
│   ├── usb_detector.py     # USB device detection
│   ├── ventoy_manager.py   # Ventoy download and installation
│   └── file_operations.py  # File copying and mounting
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## How It Works

1. **Device Detection**: Uses `lsblk` to detect USB storage devices
2. **Ventoy Download**: Downloads Ventoy v1.1.05 from GitHub releases (faster than SourceForge)
3. **Installation**: Runs `Ventoy2Disk.sh` with pkexec for secure installation
4. **File Operations**: Mounts the Ventoy partition and copies ISO files
5. **Progress Tracking**: Provides real-time updates with responsive UI using QApplication.processEvents()
6. **UI Responsiveness**: Uses QApplication.processEvents() during long operations to keep interface responsive
7. **Automatic Confirmation**: Handles Ventoy installation prompts automatically (no manual y/n input required)

## Security

- Uses `pkexec` for privilege escalation instead of sudo
- Validates all file operations before execution
- Secure temporary file handling
- No hardcoded passwords or credentials

## Troubleshooting

### Common Issues

1. **Permission Denied**: Make sure pkexec is installed and properly configured
2. **Device Not Detected**: Ensure the USB device is properly connected
3. **Ventoy Installation Fails**: Check that the device is not mounted elsewhere
4. **File Copy Errors**: Verify that the ISO files are readable and not corrupted

### Debug Mode

Run the application from terminal to see debug output:
```bash
python main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Please check the license file for details.

## Acknowledgments

- [Ventoy](https://www.ventoy.net/) for the excellent multi-boot USB tool
- [PySide6](https://doc.qt.io/qtforpython/) for the GUI framework
- Qt for the underlying UI framework

## Version History

- v1.0.0: Initial release with basic functionality
  - Modern fluent design interface
  - Ventoy installation and detection
  - Multi-ISO support
  - Progress tracking and logging
