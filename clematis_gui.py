import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QFileDialog, QCheckBox, QTextEdit, QMessageBox,
                           QMenuBar, QMenu, QAction)
from PyQt5.QtCore import Qt
import clematis
import argparse
import subprocess

class ClematisGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clematis GUI")
        self.setGeometry(100, 100, 800, 600)
        
        # Create menu
        self.create_menu()
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Input fields
        self.create_input_fields(layout)
        
        # Action buttons
        self.create_action_buttons(layout)
        
        # Output area
        self.create_output_area(layout)
        
        # Initialize variables
        self.input_file = ""
        self.output_file = ""
        
    def create_menu(self):
        menubar = self.menuBar()
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        # About action
        about_action = QAction('About Clematis', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def show_about(self):
        about_text = """
        <h2>Clematis - PE to Shellcode Converter</h2>
        
        <p><b>Description:</b></p>
        <p>Clematis is a powerful tool that converts PE (Portable Executable) files into position-independent shellcode. 
        It supports both executable files (.exe) and libraries (.dll).</p>
        
        <p><b>Supported File Types:</b></p>
        <ul>
            <li>Executable files (.exe)</li>
            <li>Dynamic Link Libraries (.dll)</li>
            <li>.NET applications</li>
            <li>Go applications</li>
        </ul>
        
        <p><b>Features:</b></p>
        <ul>
            <li>Support for x86 and x64 architectures</li>
            <li>Command-line argument support</li>
            <li>Obfuscation for enhanced stealth</li>
            <li>LZNT1 compression algorithm</li>
            <li>Automatic memory cleanup</li>
        </ul>
        
        <p><b>Usage:</b></p>
        <ol>
            <li>Select the PE file to convert</li>
            <li>Specify the output file</li>
            <li>Choose desired options (obfuscation, compression)</li>
            <li>Enter execution parameters (optional)</li>
            <li>Click "Convert to Shellcode"</li>
        </ol>
        
        <p><b>Notes:</b></p>
        <ul>
            <li>Compression is recommended for large files</li>
            <li>Obfuscation may add slight performance overhead</li>
            <li>Execution parameters should be entered as they would be given in command line</li>
        </ul>
        """
        
        QMessageBox.about(self, "About Clematis", about_text)
        
    def create_input_fields(self, layout):
        # Input file
        input_layout = QHBoxLayout()
        input_label = QLabel("Input PE File:")
        self.input_path = QLineEdit()
        self.input_path.setReadOnly(True)
        input_browse = QPushButton("Browse...")
        input_browse.clicked.connect(self.browse_input)
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_path)
        input_layout.addWidget(input_browse)
        layout.addLayout(input_layout)
        
        # Output file
        output_layout = QHBoxLayout()
        output_label = QLabel("Output File:")
        self.output_path = QLineEdit()
        self.output_path.setReadOnly(True)
        output_browse = QPushButton("Browse...")
        output_browse.clicked.connect(self.browse_output)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(output_browse)
        layout.addLayout(output_layout)
        
        # Options checkboxes
        options_layout = QHBoxLayout()
        self.garble_check = QCheckBox("Enable Obfuscation (-g)")
        self.garble_check.setChecked(True)
        self.garble_check.setToolTip(
            "Enables obfuscation of the PE file and parameters.\n"
            "This makes the shellcode harder to analyze and detect.\n"
            "May add slight performance overhead."
        )
        self.compress_check = QCheckBox("Enable Compression (-c)")
        self.compress_check.setChecked(True)
        self.compress_check.setToolTip(
            "Enables shellcode compression using LZNT1 algorithm.\n"
            "Can significantly reduce output file size.\n"
            "Recommended for large files."
        )
        options_layout.addWidget(self.garble_check)
        options_layout.addWidget(self.compress_check)
        layout.addLayout(options_layout)
        
        # Execution parameters
        params_layout = QHBoxLayout()
        params_label = QLabel("Execution Parameters (-p):")
        self.params_input = QLineEdit()
        self.params_input.setToolTip(
            "Enter the parameters that will be passed to the PE file during execution.\n"
            "For example, if your file needs parameters like:\n"
            "program.exe arg1 arg2 \"argument 3\"\n"
            "Enter here: arg1 arg2 \"argument 3\""
        )
        params_layout.addWidget(params_label)
        params_layout.addWidget(self.params_input)
        layout.addLayout(params_layout)
        
    def create_action_buttons(self, layout):
        buttons_layout = QHBoxLayout()
        self.convert_button = QPushButton("Convert to Shellcode")
        self.convert_button.clicked.connect(self.convert)
        buttons_layout.addWidget(self.convert_button)
        layout.addLayout(buttons_layout)
        
    def create_output_area(self, layout):
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)
        
    def browse_input(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select PE File", "", "Executable Files (*.exe *.dll);;All Files (*)"
        )
        if file_name:
            self.input_file = file_name
            self.input_path.setText(file_name)
            
    def browse_output(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Shellcode", "", "Binary Files (*.bin);;All Files (*)"
        )
        if file_name:
            self.output_file = file_name
            self.output_path.setText(file_name)
            
    def convert(self):
        if not self.input_file or not self.output_file:
            QMessageBox.warning(self, "Error", "Please select both input and output files")
            return
            
        try:
            # Create command line arguments
            cmd = [
                'python', 'clematis.py',
                '-f', self.input_file,
                '-o', self.output_file,
                '-g', str(self.garble_check.isChecked()).lower(),
                '-c', str(self.compress_check.isChecked()).lower()
            ]
            
            # Add execution parameters if they exist
            params = self.params_input.text().strip()
            if params:
                cmd.extend(['-p'] + params.split())
            
            # Execute conversion as separate process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for process completion
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.output_text.append("Conversion completed successfully!")
                if stdout:
                    self.output_text.append(f"Output:\n{stdout}")
            else:
                error_msg = stderr if stderr else "Unknown error occurred"
                self.output_text.append(f"Error during conversion:\n{error_msg}")
                QMessageBox.critical(self, "Error", f"Conversion failed:\n{error_msg}")
                
        except Exception as e:
            self.output_text.append(f"Error during conversion: {str(e)}")
            QMessageBox.critical(self, "Error", f"Conversion failed: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = ClematisGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 