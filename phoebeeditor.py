import sys
import os
import stat
import shutil
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QFileDialog, QMessageBox, QComboBox, QCheckBox, QTextBrowser)


class IniEditorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setting_descriptions = {
            'r.SecondaryScreenPercentage.GameViewport': 'Change Render Resolution in game (Recommended Value : 10-100).',
            'r.PostProcessAAQuality': 'Sets the Quality off AntiAliasing (Recommended Value : 0-1).',
            'r.ShadowQuality': 'Sets the Quality off Shadow. (Value : 0-3 it means Low to High).',
            'r.ViewDistanceScale': 'Sets The Render Distance object. (Value : 0.1-3 it means Low to High).',
            'r.Shadow.MaxResolution': 'Sets the Max resolution of Object. (Value : 64-4096 it means Low to High).',
            'r.Shadow.CSM.MaxCascades': 'Sets the number of shadow cascades (layers). (Value : 0-1 it means 0 = Not active , 1 = Active).',
            'r.SSR.Quality': 'Adjust the reflection quality on the screen (Screen Space Reflections).(Value 0-4 it means Low to Very High).',
            'r.BloomQuality': 'Sets the quality of the diffused light effect (bloom). (Value 0-5 it means Low to Very High).',
            'r.DefaultFeature.AmbientOcclusion': 'Sets the quality of the contact shadow effect (Ambient Occlusion). (Value 0-1 it means 0=Not Active , 1=Active).',
            'r.Reflections.Denoiser': 'Sets the denoiser quality on reflections. (Value 0-1 It means 0=Not Active , 1=Active).',
            'r.MaxAnisotropy': 'Sets the texture filtering quality. (Value 1-16 It means 1=Lowest, 4=Default, 16=Very High but Cost to Performance!).',
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
            't.MaxFPS': 'Sets the in-game frames per second (FPS) limit.(Value 30-240)',
            'r.TranslucencyVolumeBlur': 'Sets the blur for transparent objects (Value 0-1).',
            'r.ReflectionEnvironment': 'Sets the quality of the reflection environment. (Value 0-2)'
        }
        
        self.initUI()
        self.ini_file_path = ''

    def initUI(self):
        self.setWindowTitle('Graphics Editor for Wuthering Waves V0.5')
        self.setWindowIcon(QIcon('appicon.ico'))
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            bundle_dir = sys._MEIPASS
        else:
            bundle_dir = os.path.dirname(os.path.abspath(__file__))

        icon_path = os.path.join(bundle_dir, 'appicon.ico')
        self.setWindowIcon(QIcon(icon_path))
        self.setGeometry(100, 100, 650, 210)
        

        main_layout = QVBoxLayout()


        file_layout = QHBoxLayout()
        self.path_label = QLabel('File Location: Not Selected')
        self.select_button = QPushButton('Select File')
        self.select_button.clicked.connect(self.select_ini_file)

        file_layout.addWidget(self.path_label)
        file_layout.addWidget(self.select_button)
        main_layout.addLayout(file_layout)

        
        setting_layout = QHBoxLayout()
        self.key_label = QLabel('Select Settings:')
        self.setting_combo = QComboBox()
        self.setting_combo.addItems(self.setting_descriptions.keys())
        self.setting_combo.currentIndexChanged.connect(self.update_description)

        self.value_label = QLabel('New Value:')
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText('Input Value Here')

        setting_layout.addWidget(self.key_label)
        setting_layout.addWidget(self.setting_combo)
        setting_layout.addWidget(self.value_label)
        setting_layout.addWidget(self.value_input)
        main_layout.addLayout(setting_layout)
        
        
        self.info_box = QTextBrowser()
        self.info_box.setPlainText('See the description of the selected setting here.')
        main_layout.addWidget(self.info_box)

        
        self.readonly_checkbox = QCheckBox('Set the File to Read-only')
        main_layout.addWidget(self.readonly_checkbox)

        
        self.update_button = QPushButton('Update/Add Setting')
        self.update_button.clicked.connect(self.update_ini_file)
        main_layout.addWidget(self.update_button)

        self.setLayout(main_layout)
    
    def update_description(self):
        selected_key = self.setting_combo.currentText()
        description = self.setting_descriptions.get(selected_key, 'No description available.')
        self.info_box.setPlainText(description)

    def select_ini_file(self):
       
        info_text = "Default Location Of 'Engine.ini' For Wuthering Waves:\n\n"
        info_text += "Wuthering Waves\Wuthering Waves Game\Client\Saved\Config\WindowsNoEditor"
        QMessageBox.information(self, "File Location Info", info_text)
        
        fname, _ = QFileDialog.getOpenFileName(self, 'Select File Engine.ini', '', 'INI files (*.ini)')
        if fname:
            self.ini_file_path = fname
            self.path_label.setText(f'File Location: {self.ini_file_path}')
            QMessageBox.information(self, 'Success!!', 'File selected successfully.')
    
    def update_ini_file(self):
        if not self.ini_file_path:
            QMessageBox.warning(self, 'Warning', 'Please select the Engine.ini file.')
            return

        key_to_update = self.setting_combo.currentText()
        new_value = self.value_input.text().strip()
          
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

        key_to_update = self.setting_combo.currentText()
        new_value = self.value_input.text().strip()

        if not new_value:
            QMessageBox.warning(self, 'Warning', 'The value cannot be empty.')
            return

        try:
            if os.access(self.ini_file_path, os.W_OK) is False:
                os.chmod(self.ini_file_path, stat.S_IWRITE)

            with open(self.ini_file_path, 'r') as file:
                lines = file.readlines()
            
            updated = False
            has_section = False
            section_index = -1
            
            for i, line in enumerate(lines):
                if line.strip() == '[SystemSettings]':
                    has_section = True
                    section_index = i
                if line.strip().startswith(f'{key_to_update}='):
                    lines[i] = f'{key_to_update}={new_value}\n'
                    updated = True
                    break
            
            if not updated:
                if not has_section:
                    lines.insert(0, f'[SystemSettings]\n{key_to_update}={new_value}\n')
                    QMessageBox.information(self, 'Success', f'Line "{key_to_update}" Successfully added to new section.')
                else:
                    insert_index = section_index + 1
                    while insert_index < len(lines) and lines[insert_index].strip() != '' and not lines[insert_index].strip().startswith('['):
                        insert_index += 1
                    
                    lines.insert(insert_index, f'{key_to_update}={new_value}\n')
                    QMessageBox.information(self, 'Success', f'Line "{key_to_update}" Successfully Added.')
            else:
                 QMessageBox.information(self, 'Success', f'Value "{key_to_update}" Successfully changed to "{new_value}".')

            with open(self.ini_file_path, 'w') as file:
                file.writelines(lines)

            if self.readonly_checkbox.isChecked():
                os.chmod(self.ini_file_path, stat.S_IREAD)
                QMessageBox.information(self, 'Success', 'File successfully Set to Read-Only.')

        except FileNotFoundError:
            QMessageBox.critical(self, 'Error', f'File {self.ini_file_path} Not Found!.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'There is an error: {e}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = IniEditorApp()
    ex.show()
    sys.exit(app.exec_())