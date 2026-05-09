import sys
import os
import serial
import serial.tools.list_ports
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QComboBox, QPushButton, QTextEdit, QLabel, QLineEdit,
                             QCheckBox, QMessageBox, QGroupBox)
from PyQt6.QtCore import QThread, pyqtSignal, QSettings, Qt
from PyQt6.QtGui import QPen, QColor
from PyQt6 import QtCore

AUTHOR = "TerOl&MiniMaxM25"
VERSION = "1.0.0"
DATE = "2026-05-09"


class SerialReader(QThread):
    data_received = pyqtSignal(bytes)

    def __init__(self, port: str, baudrate: int = 9600):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.running = True
        self.serial_port = None

    def run(self):
        try:
            self.serial_port = serial.Serial(self.port, self.baudrate, timeout=0.1)
            while self.running:
                if self.serial_port.in_waiting > 0:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    self.data_received.emit(data)
                QThread.msleep(10)
        except Exception as e:
            self.data_received.emit(f"Error: {e}\n")
        finally:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()

    def stop(self):
        self.running = False
        self.wait()


class ComTerminal(QWidget):
    def __init__(self):
        super().__init__()
        self.reader = None
        self.current_port = None
        self.settings = QSettings("ComTerminal", "settings")
        self.init_ui()
        self.load_settings()
        self.refresh_ports()

    def init_ui(self):
        self.setWindowTitle("COM Terminal")
        self.resize(600, 450)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        port_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.port_combo.setFixedWidth(200)

        self.baud_edit = QLineEdit("9600")
        self.baud_edit.setFixedWidth(80)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_ports)

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_port)

        port_layout.addWidget(QLabel("COM Port:"))
        port_layout.addWidget(self.port_combo)
        port_layout.addWidget(QLabel("Baud:"))
        port_layout.addWidget(self.baud_edit)
        port_layout.addWidget(self.refresh_btn)
        port_layout.addWidget(self.connect_btn)
        port_layout.addStretch()

        main_layout.addLayout(port_layout)

        received_group = QGroupBox("Received data:")
        received_group.setStyleSheet("QGroupBox { font-weight: bold; } QGroupBox { border: 2px solid gray; margin-top: 10px; padding-top: 10px; border-radius: 3px;}")
        received_layout = QVBoxLayout()
        received_controls_layout = QHBoxLayout()
        self.autoscroll_check = QCheckBox("autoscroll")
        self.autoscroll_check.setChecked(True)

        self.byte_check = QCheckBox("byte")
        self.byte_check.setChecked(False)

        self.clear_rx_btn = QPushButton("Clear")
        self.clear_rx_btn.clicked.connect(self.clear_received)

        received_controls_layout.addWidget(self.autoscroll_check)
        received_controls_layout.addWidget(self.byte_check)
        received_controls_layout.addWidget(self.clear_rx_btn)
        received_controls_layout.addStretch()

        received_layout.addLayout(received_controls_layout)

        self.received_edit = QTextEdit()
        self.received_edit.setReadOnly(True)
        self.received_edit.setStyleSheet("QTextEdit { background-color: black; color: white; }")
        received_layout.addWidget(self.received_edit)

        received_group.setLayout(received_layout)
        main_layout.addWidget(received_group)

        send_group = QGroupBox("Data to send:")
        send_group.setStyleSheet("QGroupBox { font-weight: bold; } QGroupBox { border: 2px solid gray; margin-top: 10px; padding-top: 10px; border-radius: 3px; max-height: 150px; }")
        send_layout = QVBoxLayout()
        self.send_edit = QTextEdit()
        self.send_edit.setFixedHeight(80)
        self.send_edit.setStyleSheet("QTextEdit { background-color: black; color: white; }")
        self.send_edit.textChanged.connect(self.on_text_changed)
        send_layout.addWidget(self.send_edit)

        checkbox_layout = QHBoxLayout()
        self.send_imm_check = QCheckBox("send imm")
        self.send_crlf_check = QCheckBox("send \\r\\n")
        self.send_crlf_check.setChecked(True)
        checkbox_layout.addWidget(self.send_imm_check)
        checkbox_layout.addWidget(self.send_crlf_check)
        checkbox_layout.addStretch()

        send_layout.addLayout(checkbox_layout)

        btn_layout = QHBoxLayout()
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_data)

        self.clear_tx_btn = QPushButton("Clear")
        self.clear_tx_btn.clicked.connect(self.clear_input)

        btn_layout.addWidget(self.send_btn)
        btn_layout.addWidget(self.clear_tx_btn)
        btn_layout.addStretch()

        send_layout.addLayout(btn_layout)

        send_group.setLayout(send_layout)
        main_layout.addWidget(send_group)

        info_layout = QHBoxLayout()
        info_layout.addStretch()
        info_text = QLabel(f'<a href="#">info</a>')
        info_text.setTextFormat(Qt.TextFormat.RichText)
        info_text.linkActivated.connect(self.show_info)
        info_text.setStyleSheet("cursor: hand; color: #0066cc; text-decoration: underline;")
        info_layout.addWidget(info_text)
        main_layout.addLayout(info_layout)

        self.setLayout(main_layout)

    def load_settings(self):
        baud = self.settings.value("baudrate", "9600")
        self.baud_edit.setText(baud)
        
        autoscroll = self.settings.value("autoscroll", "true")
        self.autoscroll_check.setChecked(autoscroll.lower() == "true")
        
        send_imm = self.settings.value("send_imm", "false")
        self.send_imm_check.setChecked(send_imm.lower() == "true")
        
        send_crlf = self.settings.value("send_crlf", "true")
        self.send_crlf_check.setChecked(send_crlf.lower() == "true")

    def save_settings(self):
        self.settings.setValue("baudrate", self.baud_edit.text())
        self.settings.setValue("autoscroll", str(self.autoscroll_check.isChecked()).lower())
        self.settings.setValue("send_imm", str(self.send_imm_check.isChecked()).lower())
        self.settings.setValue("send_crlf", str(self.send_crlf_check.isChecked()).lower())

    def on_text_changed(self):
        if self.send_imm_check.isChecked():
            text = self.send_edit.toPlainText()
            if text:
                last_char = text[-1]
                self.send_immediate(last_char)

    def send_immediate(self, char: str):
        if not self.reader or not self.reader.isRunning():
            return

        try:
            self.reader.serial_port.write(char.encode('utf-8'))
            self.reader.serial_port.flush()
        except Exception:
            pass

    def refresh_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(port.device)

    def show_info(self):
        QMessageBox.information(self, "Info",
            f"Author: {AUTHOR}\nVersion: {VERSION}\nDate: {DATE}")

    def connect_port(self):
        port_name = self.port_combo.currentText()
        if not port_name:
            self.received_edit.insertPlainText("Error: No port selected\n")
            return

        if self.reader and self.reader.isRunning():
            self.reader.stop()
            self.reader = None
            self.connect_btn.setText("Connect")
            return

        try:
            baudrate = int(self.baud_edit.text())
            self.reader = SerialReader(port_name, baudrate)
            self.reader.data_received.connect(self.on_data_received)
            self.reader.start()
            self.connect_btn.setText("Disconnect")
        except Exception as e:
            self.received_edit.insertPlainText(f"Error: {e}\n")

    def on_data_received(self, data):
        if isinstance(data, bytes):
            if self.byte_check.isChecked():
                byte_str = ' '.join(f'{b:02X}' for b in data)
                self.received_edit.insertPlainText('0x' + byte_str + ' ')
            else:
                try:
                    text = data.decode('utf-8', errors='replace')
                except:
                    text = data.hex()
                self.received_edit.insertPlainText(text)
        else:
            self.received_edit.insertPlainText(data)
        if self.autoscroll_check.isChecked():
            self.received_edit.verticalScrollBar().setValue(
                self.received_edit.verticalScrollBar().maximum()
            )

    def send_data(self):
        if not self.reader or not self.reader.isRunning():
            self.received_edit.insertPlainText("Error: Not connected\n")
            return

        data = self.send_edit.toPlainText()
        if not data:
            return

        try:
            data_bytes = data.encode('utf-8')
            if self.send_crlf_check.isChecked():
                data_bytes += b'\r\n'
            self.reader.serial_port.write(data_bytes)
            self.reader.serial_port.flush()
        except Exception as e:
            self.received_edit.insertPlainText(f"Error: {e}\n")

    def clear_input(self):
        self.send_edit.clear()

    def clear_received(self):
        self.received_edit.clear()

    def closeEvent(self, event):
        if self.reader and self.reader.isRunning():
            self.reader.stop()
        self.save_settings()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    window = ComTerminal()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()