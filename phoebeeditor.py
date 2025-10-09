import sys
import os
import stat
import shutil
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QFileDialog, QMessageBox, 
                             QComboBox, QCheckBox, QTextBrowser, QGroupBox)
from PyQt5.QtCore import Qt, QSize


class IniEditorApp(QWidget):
    def __init__(self):
        super().__init__()
      
        self.setting_descriptions = {
            'r.SecondaryScreenPercentage.GameViewport': 'Changes the render resolution in-game (Recommended: 10-100).',
            'r.PostProcessAAQuality': 'Sets the Anti-Aliasing quality (Recommended: 0-1).',
            'r.ShadowQuality': 'Sets the Shadow quality. (Value : 0-3 it means Low to High).',
            'r.ViewDistanceScale': 'Sets the object render distance. (Value : 0.1-3 it means Low to High).',
            'r.Shadow.MaxResolution': 'Sets the max resolution of shadows. (Value : 64-4096 it means Low to High).',
            'r.Shadow.CSM.MaxCascades': 'Sets the number of shadow cascades (layers). (Value : 0-1 means 0 = Off , 1 = On).',
            'r.SSR.Quality': 'Adjusts the reflection quality (Screen Space Reflections).(Value 0-4 means Low to Very High).',
            'r.BloomQuality': 'Sets the quality of the diffused light effect (bloom). (Value 0-5 means Low to Very High).',
            'r.DefaultFeature.AmbientOcclusion': 'Sets the quality of the contact shadow effect (Ambient Occlusion). (Value 0-1 means 0=Off , 1=On).',
            'r.Reflections.Denoiser': 'Sets the denoiser quality on reflections. (Value 0-1 means 0=Off , 1=On).',
            'r.MaxAnisotropy': 'Sets the texture filtering quality. (Value 1-16 means 1=Lowest, 4=Default, 16=Very High but high performance cost!).',
            'r.LODBias': 'Sets the texture detail level. (Value -3 - 3)',
            'folliage.DensityScale': 'Sets foliage density (Value 0.1-2).',
            'r.DetailMode': 'Setting model details and textures. (Value 0-2).',
            'r.folliage.maxLOD': 'Sets the maximum detail level for foliage.(Value 0-2)',
            'grass.densityScale': 'Sets the density of grass in the environment. (Value 0-2)',
            'r.ParticleQuality': 'Sets the quality of the particle effects (Value 0-2).',
            'r.EffectQuality': 'Sets the quality of visual effects. (Value 0-3).',
            'r.PostProcessVolumeQuality': 'Sets the quality of global post-processing effects. (Value 0-3)',
            'r.ShadingQuality': 'Sets the quality of the coloring and materials. (Value 0-3)',
            'r.LensFlareQuality': 'Sets the quality of the lens flare effect. (Value 0-3)',
            'r.LightShaftQuality': 'Sets the quality of the light rays effect. (Value 0-3)',
            't.MaxFPS': 'Sets the in-game frames per second (FPS) limit.(Value 30-240).', 
            'r.TranslucencyVolumeBlur': 'Sets the blur for transparent objects (Value 0-1).',
            'r.ReflectionEnvironment': 'Sets the quality of the reflection environment. (Value 0-2)'
        }
        
        self.initUI()
        self.ini_file_path = ''
        
        self.auto_detect_ini_file()

    def get_base_dir(self):
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.abspath(__file__))

    def auto_detect_ini_file(self):
        base_dir = self.get_base_dir()
       
        relative_path = os.path.join(
            'Wuthering Waves Game', 
            'Client', 
            'Saved', 
            'Config', 
            'WindowsNoEditor', 
            'Engine.ini'
        )
        
        potential_path = os.path.join(base_dir, relative_path)
        
        if os.path.exists(potential_path):
            self.ini_file_path = potential_path
            self.path_label.setText(f'File Location: {self.ini_file_path}')
            QMessageBox.information(
                self, 
                'Auto Detection Success', 
                'Engine.ini found and selected automatically! Ready to edit.'
            )
            self.read_current_settings()
        else:
            self.path_label.setText('File Location: Not Selected (Auto Detection Failed)')
            QMessageBox.warning(
                self, 
                'Auto Detection Failed', 
                'Engine.ini not found. Please select it manually.'
            )
            self.current_settings_browser.setPlainText("Engine.ini File Not Loaded. Please select the file.")

    def initUI(self):
        
        self.setStyleSheet(self._get_dark_stylesheet())
        
        self.setWindowTitle('Wuthering Waves Graphics Editor V0.7.5')
        self.setWindowIcon(QIcon("appicon.ico"))
        self.setGeometry(100, 100, 850, 750)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

        file_group = QGroupBox("Engine.ini File Location")
        file_group.setObjectName("fileGroup")
        file_layout = QVBoxLayout()
        
        path_button_layout = QHBoxLayout()
        self.path_label = QLabel('File Location: Not Selected')
        self.path_label.setWordWrap(True)
        
        self.select_button = QPushButton('Select File Manually')
        self.select_button.setObjectName("selectButton")
        self.select_button.clicked.connect(self.manual_select_file)
        
        self.reset_button = QPushButton('Reset to Backup')
        self.reset_button.setObjectName("resetButton")
        self.reset_button.clicked.connect(self.reset_ini_file)
        
        path_button_layout.addWidget(self.path_label, 3)
        path_button_layout.addWidget(self.select_button, 1)
        path_button_layout.addWidget(self.reset_button, 1)
        file_layout.addLayout(path_button_layout)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        status_group = QGroupBox("Current Settings Status")
        status_group.setObjectName("statusGroup")
        status_layout = QVBoxLayout()
        
        status_info_label = QLabel('All relevant settings found in Engine.ini will be displayed below.')
        status_info_label.setObjectName("statusInfoLabel")
        status_layout.addWidget(status_info_label)
        
        self.current_settings_browser = QTextBrowser()
        self.current_settings_browser.setMinimumHeight(280)
        self.current_settings_browser.setObjectName("statusBrowser")
        self.current_settings_browser.setPlainText("Status will be displayed here after Engine.ini is loaded.")
        status_layout.addWidget(self.current_settings_browser)
        
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)

        edit_group = QGroupBox("Setting Modification & Save")
        edit_group.setObjectName("editGroup")
        edit_layout = QVBoxLayout()
     
        selection_layout = QHBoxLayout()
        self.setting_combo = QComboBox()
        self.setting_combo.addItems(self.setting_descriptions.keys())
        self.setting_combo.currentIndexChanged.connect(self.update_description)
        self.setting_combo.setObjectName("settingCombo")
        
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText('Enter Value Here')
        self.value_input.setObjectName("valueInput")

        selection_layout.addWidget(QLabel('Setting Key:'))
        selection_layout.addWidget(self.setting_combo, 2)
        selection_layout.addWidget(QLabel('New Value:'))
        selection_layout.addWidget(self.value_input, 1)
        edit_layout.addLayout(selection_layout)
        
        self.info_box = QTextBrowser()
        self.info_box.setPlainText('View the description for the selected setting here.')
        self.info_box.setMaximumHeight(50)
        self.info_box.setObjectName("infoBox")
        edit_layout.addWidget(self.info_box)

        control_layout = QHBoxLayout()
        self.readonly_checkbox = QCheckBox('Set File to Read-only (Recommended after modification)')
        self.readonly_checkbox.setObjectName("readonlyCheck")
        
        self.update_button = QPushButton('UPDATE SETTING & SAVE FILE (Backup Created)')
        self.update_button.setObjectName("updateButton")
        self.update_button.clicked.connect(self.update_ini_file)
        self.update_button.setMinimumSize(QSize(0, 40)) # Ensure button is substantial

        control_layout.addWidget(self.readonly_checkbox)
        control_layout.addWidget(self.update_button)
        edit_layout.addLayout(control_layout)
        
        edit_group.setLayout(edit_layout)
        main_layout.addWidget(edit_group)

        self.setLayout(main_layout)
        self.update_description()

    def _get_dark_stylesheet(self):
        BACKGROUND_DARK = "#1f1f1f"
        BACKGROUND_MEDIUM = "#2d2d2d"
        FOREGROUND_LIGHT = "#ffffff"
        BORDER_GRAY = "#404040"
     
        PRIMARY_BLUE = "#0078d4"        
        STANDARD_BUTTON_GRAY = "#4f4f4f" 
        DANGER_RED = "#d44040"          
        return f"""
            QWidget {{
                background-color: {BACKGROUND_DARK};
                color: {FOREGROUND_LIGHT};
                font-family: Inter, sans-serif;
                font-size: 10pt;
            }}
            
            QGroupBox {{
                border: 1px solid {BORDER_GRAY};
                border-radius: 12px;
                margin-top: 20px;
                padding-top: 15px;
                padding-left: 10px;
                padding-right: 10px;
                font-size: 11pt;
                font-weight: bold;
                color: {FOREGROUND_LIGHT};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                color: {FOREGROUND_LIGHT};
                background-color: {BACKGROUND_DARK};
            }}

            QLineEdit, QComboBox {{
                border: 1px solid {BORDER_GRAY};
                border-radius: 6px;
                padding: 8px;
                background-color: {BACKGROUND_MEDIUM};
                color: {FOREGROUND_LIGHT};
                selection-background-color: {PRIMARY_BLUE};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAcAAAADCAYAAABFjX8FAAAAGklEQVQIW2NgYGAkYGJhZmBiYGVmYCAmAgA/8wEBeLd15AAAAABJRU5ErkJggg==); /* Simple white arrow */
            }}
            
            QPushButton {{
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: bold;
                color: {FOREGROUND_LIGHT}; 
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}

            /* Update Button (Primary Action) - BLUE */
            QPushButton#updateButton {{
                background-color: {PRIMARY_BLUE};
                color: {FOREGROUND_LIGHT};
            }}
            QPushButton#updateButton:hover {{
                background-color: #008cdb;
            }}

            /* Select File Button (Secondary Action) - DARK GRAY */
            QPushButton#selectButton {{
                background-color: {STANDARD_BUTTON_GRAY};
                color: {FOREGROUND_LIGHT};
            }}
            QPushButton#selectButton:hover {{
                background-color: #5c5c5c;
            }}
            
            /* Reset Button (Danger/Warning) - RED */
            QPushButton#resetButton {{
                background-color: {DANGER_RED};
                color: {FOREGROUND_LIGHT};
            }}
            QPushButton#resetButton:hover {{
                background-color: #e05050;
            }}

            QTextBrowser {{
                border: 1px solid {BORDER_GRAY};
                border-radius: 8px;
                padding: 10px;
                background-color: {BACKGROUND_MEDIUM};
                color: {FOREGROUND_LIGHT};
            }}

            QCheckBox {{
                spacing: 5px;
                color: {FOREGROUND_LIGHT};
            }}
            QCheckBox::indicator {{
                width: 15px;
                height: 15px;
                border: 1px solid {BORDER_GRAY};
                border-radius: 4px;
                background-color: {BACKGROUND_DARK};
            }}
            QCheckBox::indicator:checked {{
                background-color: {PRIMARY_BLUE};
                border: 1px solid {PRIMARY_BLUE};
                image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAcAAAAHCAYAAACzXTVzAAAAG0lEQVQIW2NgoBzcwNDS0sDAwMTAwMgAEiQJADUoAS3pX+0eAAAAAElFTkSuQmCC); /* Small white checkmark */
            }}
            
            QLabel {{
                color: #e0e0e0;
            }}
            QLabel#statusInfoLabel {{
                    color: #aaaaaa;
            }}
        """

    def read_current_settings(self):
        if not self.ini_file_path or not os.path.exists(self.ini_file_path):
            self.current_settings_browser.setHtml(
                "<span style='color: #ff4500;'>Engine.ini file not loaded or found.</span>"
            )
            return

        target_keys = set(self.setting_descriptions.keys())
        in_system_settings = False
        found_settings = {} 

        try:
            with open(self.ini_file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line_strip = line.strip()
                    
                    if line_strip == '[SystemSettings]':
                        in_system_settings = True
                        continue
                    
                    if line_strip.startswith('[') and line_strip.endswith(']'):
                      
                        if in_system_settings:
                           in_system_settings = False
                           
                    if in_system_settings and '=' in line_strip and not line_strip.startswith(';'):
                        try:
                            key, value = line_strip.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            if key in target_keys:
                                found_settings[key] = value
                        except ValueError:
                            continue

            self.display_settings(found_settings)

        except Exception as e:
            self.current_settings_browser.setHtml(
                f"<span style='color: #ff4500;'>Error reading file: {e}</span>"
            )

    def display_settings(self, settings):
        display_html = "<span style='font-size: 11pt; color: #0078d4;'>Configured Settings:</span><br><br>"
        
        if not settings:
            display_html += "<span style='color: #ffb900;'>No relevant settings found or they are not under the [SystemSettings] section.</span>"
        else:
            sorted_keys = sorted(settings.keys())
            
            for key in sorted_keys:
                value = settings[key]
                
                display_html += f"<b><span style='color: #ffffff;'>{key}</span></b><br>"
                display_html += f"  <span style='color: #a0a0a0;'>&gt; Current Value: {value}</span><br>" 
                display_html += "<span style='color: #404040;'>--------------------------------------------------</span><br>"

        self.current_settings_browser.setHtml(display_html)
    
    def update_description(self):
        selected_key = self.setting_combo.currentText()
        description = self.setting_descriptions.get(selected_key, 'No description available.')
        self.info_box.setPlainText(description)

    def manual_select_file(self):
        info_text = "Default Location Of 'Engine.ini' For Wuthering Waves:\n\n"
        info_text += "Wuthering Waves\\Wuthering Waves Game\\Client\\Saved\\Config\\WindowsNoEditor"
        QMessageBox.information(self, "File Location Info", info_text)
        
        start_dir = self.get_base_dir()
        
        fname, _ = QFileDialog.getOpenFileName(self, 'Select Engine.ini File', start_dir, 'INI files (*.ini)')
        if fname:
            self.ini_file_path = fname
            self.path_label.setText(f'File Location: {self.ini_file_path}')
            QMessageBox.information(self, 'Success!!', 'File selected successfully. Loading current status.')
            self.read_current_settings()
        else:
            self.ini_file_path = ''
            self.path_label.setText('File Location: Not Selected')
            self.current_settings_browser.setPlainText("Engine.ini file not loaded. Please select the file.")
    
    def update_ini_file(self):
        if not self.ini_file_path:
            QMessageBox.warning(self, 'Warning', 'Please select the Engine.ini file.')
            return

        key_to_update = self.setting_combo.currentText()
        new_value = self.value_input.text().strip()
            
        if not new_value:
            QMessageBox.warning(self, 'Warning', 'The value cannot be empty.')
            return

     
        try:
            ini_dir = os.path.dirname(self.ini_file_path)
            backup_dir = os.path.join(ini_dir, 'backup')
            
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            backup_filename = 'Engine_backup.ini'
            backup_path = os.path.join(backup_dir, backup_filename)
            
            shutil.copyfile(self.ini_file_path, backup_path)
            QMessageBox.information(self, 'Backup Created', f'A backup of the file has been created at:\n{backup_path}\nPrevious backup was overwritten.')
        except Exception as e:
            QMessageBox.critical(self, 'Backup Error', f'Failed to create backup: {e}')
            return

        try:
            
            if not os.access(self.ini_file_path, os.W_OK):
                
                current_mode = os.stat(self.ini_file_path).st_mode
                os.chmod(self.ini_file_path, current_mode | stat.S_IWRITE)

            with open(self.ini_file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            updated = False
            has_system_settings_section = False
            section_index = -1
            
            for i, line in enumerate(lines):
                line_strip = line.strip()
                if line_strip == '[SystemSettings]':
                    has_system_settings_section = True
                    section_index = i
                    continue
                
                
                if has_system_settings_section:
                    if line_strip.startswith('[') and line_strip.endswith(']'):
                        
                         has_system_settings_section = False
                         
                    elif line_strip.startswith(f'{key_to_update}='):
                        lines[i] = f'{key_to_update}={new_value}\n'
                        updated = True
                        break 
       
            if not updated:
                new_line = f'{key_to_update}={new_value}\n'
                
                if not has_system_settings_section and section_index == -1:
                    
                    lines.append(f'\n[SystemSettings]\n{new_line}')
                    QMessageBox.information(self, 'Success', f'Line "{key_to_update}" added to a new [SystemSettings] section.')
                else:
                    
                    insert_index = section_index + 1
                    
                    lines.insert(insert_index, new_line)
                    QMessageBox.information(self, 'Success', f'Line "{key_to_update}" Successfully Added to [SystemSettings].')
            else:
                QMessageBox.information(self, 'Success', f'Value "{key_to_update}" Successfully changed to "{new_value}".')

            with open(self.ini_file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)

            if self.readonly_checkbox.isChecked():
                os.chmod(self.ini_file_path, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH) # Set read-only permissions
                QMessageBox.information(self, 'Success', 'File successfully Set to Read-Only.')
            
            self.read_current_settings()

        except FileNotFoundError:
            QMessageBox.critical(self, 'Error', f'File {self.ini_file_path} Not Found!.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'There is an error: {e}')

    def reset_ini_file(self):
        if not self.ini_file_path:
            QMessageBox.warning(self, 'Warning', 'Please select the Engine.ini file first.')
            return

        ini_dir = os.path.dirname(self.ini_file_path)
        backup_path = os.path.join(ini_dir, 'backup', 'Engine_backup.ini')

        if not os.path.exists(backup_path):
            QMessageBox.critical(self, 'Error', f'Backup file not found at: {backup_path}\nMake sure you have saved settings at least once.')
            return

        reply = QMessageBox.question(
            self, 
            'Confirmation', 
            'Are you sure you want to restore Engine.ini from the last backup? This will overwrite the current file.',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )

        if reply == QMessageBox.No:
            return

        try:
          
            if not os.access(self.ini_file_path, os.W_OK):
                current_mode = os.stat(self.ini_file_path).st_mode
                os.chmod(self.ini_file_path, current_mode | stat.S_IWRITE)

            shutil.copyfile(backup_path, self.ini_file_path)
          
            self.read_current_settings()
            QMessageBox.information(self, 'Success', 'Engine.ini successfully restored from backup and current status reloaded.')

        except Exception as e:
            QMessageBox.critical(self, 'Reset Error', f'Failed to restore file: {e}')
            return

if __name__ == '__main__':
 
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
    app = QApplication(sys.argv)
    ex = IniEditorApp()
    ex.show()
    sys.exit(app.exec_())
