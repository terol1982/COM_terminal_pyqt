# COM Terminal - Specification

## Project Overview
- **Project name**: COM Terminal
- **Type**: Desktop application (Windows)
- **Core functionality**: Serial communication via COM ports with GUI
- **Target users**: Developers, hardware engineers
- **Author**: TerOl&MiniMaxM25
- **Version**: 1.0.0
- **Date**: 2026-05-09

## UI/UX Specification

### Layout Structure
- **Window**: Resizable main window (default 600x450)
- **Layout**: Vertical QVBoxLayout with spacing

### Visual Design
- **Background**: Default Qt style
- **Text fields (Received/Send)**: Black background with white text
- **Group boxes**: 2px solid gray border with rounded corners
- **Font**: Default system font
- **Spacing**: 10px between elements

### Components

1. **COM Port Selection Area** (horizontal layout)
   - QComboBox for COM port selection (width: 200px)
   - QLineEdit for baud rate (default: 9600, width: 80px)
   - QPushButton "Refresh"
   - QPushButton "Connect/Disconnect"

2. **Received Data Area** (QGroupBox with bold title)
   - QCheckBox "autoscroll" (enabled by default)
   - QCheckBox "byte" (for hex display)
   - QPushButton "Clear"
   - QTextEdit (read-only, black background, white text)

3. **Send Data Area** (QGroupBox with bold title)
   - QTextEdit (black background, white text, height: 80px)
   - QCheckBox "send imm" (immediate send on typing)
   - QCheckBox "send \r\n" (append newline, enabled by default)
   - QPushButton "Send"
   - QPushButton "Clear"

4. **Info Link**
   - QLabel "info" (clickable link in bottom-right)
   - Opens QMessageBox with Author, Version, Date

## Functionality Specification

### Core Features
1. **Port Discovery**: Enumerate available COM ports on startup and refresh
2. **Port Connection**: Connect to selected port with configurable baud rate
3. **Data Reception**: Display received data (text or hex mode)
4. **Data Transmission**: Send text to port (with optional newline)
5. **Immediate Send**: Send characters as they are typed
6. **Auto-scroll**: Automatically scroll to bottom (toggleable)
7. **Settings**: Persist settings between sessions (QSettings)

### User Interactions
- Select COM port from dropdown
- Set baud rate in text field
- Click "Refresh" to update port list
- Click "Connect" to connect to port
- Type data in send field
- Click "Send" or enable "send imm" for immediate send
- Toggle "byte" to display received data as hex
- Toggle "autoscroll" for auto-scrolling
- Click "info" to view program info

### Data Handling
- Receive: Raw bytes, display as text or hex with "0x" prefix
- Send: UTF-8 encoding, optional CRLF append

## Acceptance Criteria
1. Application launches without errors
2. COM ports are listed in dropdown
3. Refresh button updates port list
4. Connect button establishes serial connection
5. Data can be sent to selected port
6. Received data appears in display field
7. Byte mode displays hex representation
8. Immediate send works on keypress
9. Settings persist between sessions
10. Info dialog shows version info