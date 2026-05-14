from __future__ import annotations

import sys
import datetime
import serial
import serial.tools.list_ports
from dataclasses import dataclass, field
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QPushButton, QTextEdit, QLabel, QLineEdit,
    QCheckBox, QMessageBox, QGroupBox, QFileDialog
)
from PyQt6.QtCore import QThread, pyqtSignal, QSettings, Qt, QTime


AUTHOR = "TerOl&MiniMaxM25"
VERSION = "1.1.2"
DATE = "2026-05-14"
GIT = "https://github.com/terol1982/COM_terminal_pyqt"


@dataclass
class AppInfo:
    author: str = AUTHOR
    version: str = VERSION
    GIT: str = GIT
    date: str = DATE


@dataclass
class AppSettings:
    baudrate: str = "9600"
    autoscroll: bool = True
    time_show: bool = False
    send_imm: bool = False
    send_crlf: bool = True
    nl_text: str = "\\n"


class SerialReader(QThread):
    data_received = pyqtSignal(bytes)

    def __init__(self, port: str, baudrate: int = 9600) -> None:
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.running = True
        self.serial_port: Optional[serial.Serial] = None

    def run(self) -> None:
        try:
            self.serial_port = serial.Serial(self.port, self.baudrate, timeout=0.1)
            while self.running:
                if self.serial_port.in_waiting > 0:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    self.data_received.emit(data)
                QThread.msleep(10)
        except serial.SerialException as e:
            self.data_received.emit(f"Error: {e}\n".encode('utf-8'))
        finally:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()

    def stop(self) -> None:
        self.running = False
        self.wait()


class ComTerminal(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.reader: Optional[SerialReader] = None
        self.new_data: bool = True
        self.settings = QSettings("ComTerminal", "settings")
        self.init_ui()
        self.load_settings()
        self.refresh_ports()

    def init_ui(self) -> None:
        self.setWindowTitle("COM Terminal")
        self.resize(600, 450)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        port_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.port_combo.setFixedWidth(100)
        self.port_combo.setStyleSheet("QComboBox { border: 1px solid gray; border-radius: 3px; padding:2px}")

        self.baud_edit = QLineEdit("9600")
        self.baud_edit.setFixedWidth(80)
        self.baud_edit.setStyleSheet("QLineEdit { border: 1px solid gray; border-radius: 3px; padding:2px}")

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        self.refresh_btn.setStyleSheet("QPushButton { border: 1px solid gray; border-radius: 3px; padding:2px; }")

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_port)
        self.connect_btn.setStyleSheet("QPushButton { border: 1px solid gray; border-radius: 3px; padding:2px; }")
        self.connect_btn.setToolTip("Disconnected. Click to connect.")

        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("QLabel { color: red; font-size: 25px; padding-top:0px; margin-top: -8px;}")

        port_layout.addWidget(QLabel("COM Port:"))
        port_layout.addWidget(self.port_combo)
        port_layout.addWidget(QLabel("Baud:"))
        port_layout.addWidget(self.baud_edit)
        port_layout.addWidget(self.refresh_btn)
        port_layout.addWidget(self.connect_btn)
        port_layout.addWidget(self.status_indicator)
        port_layout.addStretch()

        main_layout.addLayout(port_layout)

        received_group = QGroupBox("Received data:")
        received_group.setStyleSheet("QGroupBox { border: 1px solid gray; padding-top: 10px; border-radius: 3px;}")
        received_layout = QVBoxLayout()
        received_controls_layout = QHBoxLayout()
        self.autoscroll_check = QCheckBox("autoscroll")
        self.autoscroll_check.setChecked(True)

        self.byte_check = QCheckBox("As Bytes")
        self.byte_check.setToolTip("Show data as bytes")
        self.byte_check.setChecked(False)

        self.time_show_check = QCheckBox("show time")
        self.time_show_check.setChecked(False)

        self.clear_rx_btn = QPushButton("Clear")
        self.clear_rx_btn.clicked.connect(self.clear_received)
        self.clear_rx_btn.setStyleSheet("QPushButton { border: 1px solid gray; border-radius: 3px; padding:2px; }")


        self.save_rx_btn = QPushButton("Save to file")
        self.save_rx_btn.clicked.connect(self.save_received)
        self.save_rx_btn.setStyleSheet("QPushButton { border: 1px solid gray; border-radius: 3px; padding:2px; }")



        received_controls_layout.addWidget(self.autoscroll_check)
        received_controls_layout.addWidget(self.byte_check)
        received_controls_layout.addWidget(self.time_show_check)
        received_controls_layout.addWidget(self.clear_rx_btn)
        received_controls_layout.addWidget(self.save_rx_btn)
        received_controls_layout.addStretch()

        received_layout.addLayout(received_controls_layout)

        self.received_edit = QTextEdit()
        self.received_edit.setReadOnly(True)
        self.received_edit.setStyleSheet("QTextEdit { background-color: black; color: white; border-radius: 3px;}")
        received_layout.addWidget(self.received_edit)

        received_group.setLayout(received_layout)
        main_layout.addWidget(received_group)

        send_group = QGroupBox("Data to send:")
        send_group.setStyleSheet("QGroupBox { border: 1px solid gray; padding-top:10px; border-radius: 3px; max-height: 150px; }")
        send_layout = QVBoxLayout()
        send_group.setCheckable(True)
        send_group.setChecked(True)
        send_group.toggled.connect(self._toggle_send_group)

        self.send_edit = QTextEdit()
        self.send_edit.setFixedHeight(80)
        self.send_edit.setStyleSheet("QTextEdit { background-color: black; color: white; border-radius: 3px;}")
        self.send_edit.textChanged.connect(self.on_text_changed)
        send_layout.addWidget(self.send_edit)

        checkbox_layout = QHBoxLayout()
        self.send_imm_check = QCheckBox("send imm")
        self.send_imm_check.setToolTip("Send data immediately as you type")
        self.send_crlf_check = QCheckBox("add new line symbol:")
        self.send_crlf_check.setToolTip("Add newline character when Send button is clicked")
        self.send_crlf_check.setChecked(True)
        self.nl_edit = QLineEdit("\\n")
        self.nl_edit.setMaximumWidth(60)
        self.nl_edit.setToolTip("Newline suffix (e.g. \\n, \\r\\n)")
        checkbox_layout.addWidget(self.send_imm_check)
        checkbox_layout.addWidget(self.send_crlf_check)
        #checkbox_layout.addWidget(QLabel())
        checkbox_layout.addWidget(self.nl_edit)
        checkbox_layout.addStretch()

        send_layout.addLayout(checkbox_layout)

        btn_layout = QHBoxLayout()
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_data)
        self.send_btn.setStyleSheet("QPushButton { border: 1px solid gray; border-radius: 3px; padding:2px; }")

        self.clear_tx_btn = QPushButton("Clear")
        self.clear_tx_btn.clicked.connect(self.clear_input)
        self.clear_tx_btn.setStyleSheet("QPushButton { border: 1px solid gray; border-radius: 3px; padding:2px; }")


        btn_layout.addWidget(self.send_btn)
        btn_layout.addWidget(self.clear_tx_btn)
        btn_layout.addStretch()

        send_layout.addLayout(btn_layout)

        send_group.setLayout(send_layout)
        main_layout.addWidget(send_group)

        info_layout = QHBoxLayout()
        info_layout.addStretch()
        info_text = QLabel('<a href="#">info</a>')
        info_text.setTextFormat(Qt.TextFormat.RichText)
        info_text.linkActivated.connect(self.show_info)
        info_text.setStyleSheet("color: #0066cc; text-decoration: underline;")
        info_layout.addWidget(info_text)
        main_layout.addLayout(info_layout)

        self.setLayout(main_layout)

    def load_settings(self) -> None:
        app_settings = AppSettings(
            baudrate=self.settings.value("baudrate", "9600"),
            autoscroll=self.settings.value("autoscroll", True, type=bool),
            time_show=self.settings.value("time_show", False, type=bool),
            send_imm=self.settings.value("send_imm", False, type=bool),
            send_crlf=self.settings.value("send_crlf", True, type=bool),
            nl_text=self.settings.value("nl_text", "\\n"),
        )
        self.baud_edit.setText(app_settings.baudrate)
        self.autoscroll_check.setChecked(app_settings.autoscroll)
        self.time_show_check.setChecked(app_settings.time_show)
        self.send_imm_check.setChecked(app_settings.send_imm)
        self.send_crlf_check.setChecked(app_settings.send_crlf)
        self.nl_edit.setText(app_settings.nl_text)

    def save_settings(self) -> None:
        self.settings.setValue("baudrate", self.baud_edit.text())
        self.settings.setValue("autoscroll", self.autoscroll_check.isChecked())
        self.settings.setValue("time_show", self.time_show_check.isChecked())
        self.settings.setValue("send_imm", self.send_imm_check.isChecked())
        self.settings.setValue("send_crlf", self.send_crlf_check.isChecked())
        self.settings.setValue("nl_text", self.nl_edit.text())

    def _toggle_send_group(self, checked: bool) -> None:
        self.send_edit.setVisible(checked)
        self.send_imm_check.setVisible(checked)
        self.send_crlf_check.setVisible(checked)
        self.nl_edit.setVisible(checked)
        self.send_btn.setVisible(checked)
        self.clear_tx_btn.setVisible(checked)

    def on_text_changed(self) -> None:
        if self.send_imm_check.isChecked():
            text = self.send_edit.toPlainText()
            if text:
                last_char = text[-1]
                self._send_immediate(last_char)

    def _send_immediate(self, char: str) -> None:
        if self.reader is None or not self.reader.isRunning():
            return

        try:
            self.reader.serial_port.write(char.encode('utf-8'))
            self.reader.serial_port.flush()
        except serial.SerialException:
            pass

    def refresh_ports(self) -> None:
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(port.device)

    def show_info(self) -> None:
        info = AppInfo()
        msg_box = QMessageBox()
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(
            f"Author: {info.author}\n<br/>Version: {info.version}\n<br/>GitHub: <a href='{info.GIT}'>{info.GIT}</a>\n<br/>Date: {info.date}"
        )
        msg_box.setWindowTitle("Info")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        

    def connect_port(self) -> None:
        port_name = self.port_combo.currentText()
        if not port_name:
            self.received_edit.insertPlainText("Error: No port selected\n")
            return

        if self.reader is not None and self.reader.isRunning():
            self.reader.stop()
            self.reader = None
            self._reset_connect_state()
            return

        try:
            baudrate = int(self.baud_edit.text())
            self.reader = SerialReader(port_name, baudrate)
            self.reader.data_received.connect(self.on_data_received)
            self.reader.start()
            self.connect_btn.setText("Disconnect")
            self.connect_btn.setToolTip("Connected. Click to disconnect.")
            # self.connect_btn.setStyleSheet(
            #     "QPushButton { background-color: green; color: white; border: 1px solid green; border-radius: 3px; padding:2px;}"
            #     "QPushButton:hover { background-color: green; border: 2px solid green;}"
            # )
            self.refresh_btn.setEnabled(False)
            self.status_indicator.setStyleSheet("QLabel { color: green; font-size: 25px; padding-top:0px; margin-top: -8px;}")
        except ValueError as e:
            self.received_edit.insertPlainText(f"Error: Invalid baud rate: {e}\n")
        except serial.SerialException as e:
            self.received_edit.insertPlainText(f"Error: {e}\n")
            self._reset_connect_state()

    def _reset_connect_state(self) -> None:
        self.reader = None
        self.connect_btn.setText("Connect")
        self.connect_btn.setToolTip("Disconnected. Click to connect.")
        # self.connect_btn.setStyleSheet(
        #     "QPushButton { background-color: red; color: white; border: 1px solid red; border-radius: 3px; padding:2px;}"
        #     "QPushButton:hover { background-color: red; border: 2px solid red;}"
        # )
        self.status_indicator.setStyleSheet("QLabel { color: red; font-size: 25px; padding-top:0px; margin-top: -8px;}")
        self.refresh_btn.setEnabled(True)
        self.refresh_ports()

    def on_data_received(self, data: bytes) -> None:
        error_str = "Error:"
        if data.startswith(error_str.encode('utf-8')):
            error_text = data.decode('utf-8', errors='replace')
            self.received_edit.insertPlainText(error_text)
            self._reset_connect_state()
            return

        if self.byte_check.isChecked():
            for b in data:
                self.received_edit.insertPlainText(f'0x{b:02X} ')
        else:
            try:
                text = data.decode('utf-8', errors='replace')
            except UnicodeDecodeError:
                text = data.hex()

            text = text.replace('\r\n', '\n')

            for char in text:
                if self.new_data and self.time_show_check.isChecked():
                    timestamp = QTime.currentTime().toString("hh:mm:ss:zzz")
                    self.received_edit.insertPlainText(f"[{timestamp}]")
                    self.new_data = False
                self.received_edit.insertPlainText(char)
                if char == '\n':
                    self.new_data = True

        if self.autoscroll_check.isChecked():
            scroll_bar = self.received_edit.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.maximum())

    def send_data(self) -> None:
        if self.reader is None or not self.reader.isRunning():
            self.received_edit.insertPlainText("Error: Not connected\n")
            return

        data = self.send_edit.toPlainText()
        if not data:
            return

        try:
            nl_text = self.nl_edit.text().encode('utf-8').decode('unicode_escape').encode('latin-1')
            data_bytes = data.encode('utf-8') + nl_text if self.send_crlf_check.isChecked() else data.encode('utf-8')
            self.reader.serial_port.write(data_bytes)
            self.reader.serial_port.flush()
        except serial.SerialException as e:
            self.received_edit.insertPlainText(f"Error: {e}\n")

    def clear_input(self) -> None:
        self.send_edit.clear()

    def clear_received(self) -> None:
        self.received_edit.clear()

    def save_received(self) -> None:
        filename = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".txt"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Received Data", filename, "Text Files (*.txt)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.received_edit.toPlainText())
            except OSError as e:
                QMessageBox.warning(self, "Error", f"Failed to save file: {e}")

    def closeEvent(self, event) -> None:
        if self.reader is not None and self.reader.isRunning():
            self.reader.stop()
        self.save_settings()
        self.refresh_btn.setEnabled(True)
        super().closeEvent(event)


def main() -> None:
    app = QApplication(sys.argv)
    window = ComTerminal()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
