# COM Port Terminal - Specification

## Project Overview
- **Project name**: COM Port Terminal
- **Type**: Desktop application (Windows)
- **Core functionality**: Serial communication via COM ports with GUI
- **Target users**: Developers, hardware engineers

## UI/UX Specification

### Layout Structure
- **Window**: Single main window, 600x450 pixels, non-resizable
- **Layout**: Vertical QVBoxLayout with spacing

### Visual Design
- **Color scheme**: 
  - Background: #f5f5f5 (light gray)
  - Text fields: white background
  - Buttons: default Qt style
- **Font**: Default system font
- **Spacing**: 10px between elements

### Components
1. **COM Port Selection Area** (horizontal layout)
   - QComboBox for COM port selection (width: 200px)
   - QPushButton "Оновити" (Refresh)

2. **Received Data Area**
   - QLabel "Отримані дані:"
   - QTextEdit (read-only, height: 150px)

3. **Send Data Area**
   - QLabel "Дані для відправки:"
   - QTextEdit (editable, height: 80px)

4. **Send Button**
   - QPushButton "Відправити"

### Component States
- ComboBox: enabled when ports available, disabled otherwise
- Buttons: default enabled state
- TextEdit for received: read-only, selectable

## Functionality Specification

### Core Features
1. **Port Discovery**: Enumerate available COM ports on startup and refresh
2. **Port Connection**: Auto-connect to selected port at 9600 baud, 8N1
3. **Data Reception**: Display received data in read-only text field
4. **Data Transmission**: Send text from input field to port

### User Interactions
1. Select COM port from dropdown
2. Click "Оновити" to refresh port list
3. Type data in input field
4. Click "Відправити" to send data

### Data Handling
- Receive: Accumulate in buffer, display with newline
- Send: Convert to bytes, append newline

## Acceptance Criteria
1. Application launches without errors
2. COM ports are listed in dropdown
3. Refresh button updates port list
4. Data can be sent to selected port
5. Received data appears in display field