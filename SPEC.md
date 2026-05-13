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
- **Group boxes**: 1px solid gray border with rounded corners
- **Font**: Default system font
- **Spacing**: 10px between elements

### Components

1. **COM Port Selection Area** (horizontal layout)
   - QComboBox for COM port selection (width: 100px)
   - QLineEdit for baud rate (default: 9600, width: 80px)
   - QPushButton "Refresh" (disabled when connected)
   - QPushButton "Connect/Disconnect" (red=disconnected, green=connected)
   - QLabel "●" status indicator (red=disconnected, green=connected)

2. **Received Data Area** (QGroupBox with bold title)
   - QCheckBox "autoscroll" (enabled by default)
   - QCheckBox "byte" (for hex display)
   - QCheckBox "show time" (display timestamp before each line)
   - QPushButton "Clear"
   - QPushButton "Save to file"
   - QTextEdit (read-only, black background, white text)

3. **Send Data Area** (QGroupBox with bold title, collapsible)
   - QTextEdit (black background, white text, height: 80px)
   - QCheckBox "send imm" (immediate send on typing)
   - QCheckBox "send \n" (append newline, enabled by default)
   - QLineEdit "NL:" with custom newline suffix (default: "\n")
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
4. **Data Transmission**: Send text to port (with configurable newline suffix)
5. **Immediate Send**: Send characters as they are typed
6. **Auto-scroll**: Automatically scroll to bottom (toggleable)
7. **Settings**: Persist settings between sessions (QSettings) - baudrate, autoscroll, time_show, send_imm, send_crlf, nl_text
8. **Line Ending Normalization**: Replace `\r\n` with `\n` in received text
9. **Connection State Management**: Automatic UI reset on connection error
10. **Custom Newline**: Configurable newline suffix (supports escape sequences like \n, \r\n, \t)

### Connection State Machine
| State | Refresh Button | Connect Button |
|-------|---------------|----------------|
| Disconnected | Enabled | Red, "Disconnected" |
| Connecting | Disabled | Green, "Connected" |
| Connection Error | Enabled | Red, "Disconnected" + refresh port list |
| Disconnecting | Enabled | Red, "Disconnected" |

### User Interactions
- Select COM port from dropdown
- Set baud rate in text field
- Click "Refresh" to update port list
- Click "Connect" to connect to port (disables Refresh)
- Type data in send field
- Click "Send" or enable "send imm" for immediate send
- Toggle "byte" to display received data as hex
- Toggle "autoscroll" for auto-scrolling
- Click "info" to view program info
- On connection error: UI auto-resets and refreshes port list

### Data Handling
- Receive: Raw bytes, display as text or hex with "0x" prefix
- Send: UTF-8 encoding, optional custom newline suffix (supports escape sequences)
- Line endings: `\r\n` normalized to `\n` in text mode

### Error Handling
- Invalid baud rate: Display error in received field
- Serial port error: Display error, reset UI state, refresh port list
- File save error: Show warning dialog

## Acceptance Criteria
1. Application launches without errors
2. COM ports are listed in dropdown
3. Refresh button updates port list
4. Connect button establishes serial connection
5. Status indicator shows connection state (green/red)
6. Data can be sent to selected port
7. Received data appears in display field
8. Byte mode displays hex representation
9. Immediate send works on keypress
10. Custom NL field appends configurable newline suffix
11. Settings persist between sessions (including nl_text)
12. Info dialog shows version info
13. Refresh button disabled when connected
14. UI resets automatically on connection error
15. `\r\n` replaced with `\n` in received text
