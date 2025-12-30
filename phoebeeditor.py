import sys
import os
import stat
import shutil
import platform
try:
    import pyi_splash
    _PYI_SPLASH = pyi_splash
except Exception:
    _PYI_SPLASH = None
    
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFileDialog, QMessageBox, 
                             QCheckBox, QScrollArea, QFrame, QSlider, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

SETTINGS_CONFIG = {
    'r.SecondaryScreenPercentage.GameViewport': [10, 100, 1, 'This is a 3D render resolution'],
    'r.PostProcessAAQuality': [0, 6, 1, 'Control the smoothness of jagged edges in the game visuals'],
    'r.ShadowQuality': [0, 3, 1, 'Shadow Quality determines the realism ,sharpness, and detail of shadows'],
    'r.ViewDistanceScale': [1, 30, 10, 'Object View Distance Scale acts as a global multiplier for the maximum distance at which objects are rendered  '],
    'r.Shadow.MaxResolution': [64, 4096, 1, 'The Shadow Max resolution determines of sharpness of shadows'],
    'r.Shadow.CSM.MaxCascades': [0, 4, 1, 'Shadow Cascades improve the quality of shadows over distance '],
    'r.SSR.Quality': [0, 4, 1, 'Screen Space Reflections is a technique used to create real-time reflections in 3D environments'],
    'r.BloomQuality': [0, 5, 1, 'Bloom Effect Quality determines the intensity and quality of the bloom effect'],
    'r.DefaultFeature.AmbientOcclusion': [0, 1, 1, 'Ambient Occlusion adds depth and realism to scenes by simulating the way light interacts with surfaces'],
    'r.MaxAnisotropy': [1, 16, 1, 'Texture Filtering Anisotropy improves the clarity and sharpness of textures viewed at oblique angles'],
    'r.LODBias': [-3, 3, 1, 'LOD Bias adjusts the level of detail for 3D models '],
    'folliage.DensityScale': [1, 20, 10, 'Foliage Density Scale controls the amount of vegetation rendered in the game world'],
    't.MaxFPS': [30, 240, 1, 'In-game FPS Limit'],
    'r.ParticleQuality': [0, 2, 1, 'Particle Effects Quality determines the complexity and detail of particle effects'],
    'r.EffectQuality': [0, 3, 1, 'Visual Effects Quality controls the overall quality of various visual effects'],
    'r.ShadingQuality': [0, 3, 1, 'Shading/Material Quality affects the realism and detail of surface materials'],
}

class SettingCard(QFrame):
    def __init__(self, key, config, current_val=None):
        super().__init__()
        self.key = key
        self.min, self.max, self.mult, self.desc = config
        self.setObjectName("SettingCard")
        
        layout = QVBoxLayout(self)
      
        header_layout = QHBoxLayout()
        self.label_name = QLabel(key)
        self.label_name.setStyleSheet("font-weight: bold; color: #00d4ff;")
        
        self.label_val = QLabel(str(current_val if current_val else self.min))
        self.label_val.setStyleSheet("font-weight: bold; color: #ffffff; background: #333; padding: 2px 8px; border-radius: 4px;")
        
        header_layout.addWidget(self.label_name)
        header_layout.addStretch()
        header_layout.addWidget(self.label_val)
        
        self.label_desc = QLabel(self.desc)
        self.label_desc.setStyleSheet("color: #aaaaaa; font-size: 9pt;")
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(self.min)
        self.slider.setMaximum(self.max)
        
        try:
            val = float(current_val) * self.mult if current_val else self.min
            self.slider.setValue(int(val))
        except:
            self.slider.setValue(self.min)

        self.slider.valueChanged.connect(self.update_label)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.label_desc)
        layout.addWidget(self.slider)

    def update_label(self, value):
        display_val = value / self.mult if self.mult != 1 else value
        self.label_val.setText(str(display_val))

    def get_value(self):
        val = self.slider.value()
        return str(val / self.mult if self.mult != 1 else val)

class ModernWavesEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.ini_file_path = ''
        self.cards = {}
        self.pc_name = platform.node()
        self.initUI()
        self.auto_detect_ini_file()

    def initUI(self):
        self.setWindowTitle('Wuthering Waves Graphics Tweaker 0.8')
        icon_path = resource_path('picture/lynae.ico')
        self.setWindowIcon(QIcon(resource_path('picture/lynae.ico')))
        self.resize(1000, 550)
        self.setStyleSheet(self._get_stylesheet())

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel(f"Welcome To Graphics Tweaker {self.pc_name}")
        title.setStyleSheet("font-size: 22pt; font-weight: bold; color: white; margin-bottom: 5px;")
        main_layout.addWidget(title)

        self.path_card = QFrame()
        self.path_card.setObjectName("PathCard")
        path_layout = QHBoxLayout(self.path_card)
        self.path_label = QLabel('Path: Not Selected')
        self.path_label.setWordWrap(True)
        self.btn_select = QPushButton("Browse")
        self.btn_select.clicked.connect(self.manual_select_file)
        path_layout.addWidget(self.path_label, 4)
        path_layout.addWidget(self.btn_select, 1)
        main_layout.addWidget(self.path_card)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(15)
        self.scroll.setWidget(self.scroll_widget)
        main_layout.addWidget(self.scroll)

        bottom_layout = QVBoxLayout()
        self.check_readonly = QCheckBox("Lock file as Read-Only after saving")
        self.btn_save = QPushButton("APPLY ALL CHANGES")
        self.btn_save.setObjectName("BtnSave")
        self.btn_save.setFixedHeight(50)
        self.btn_save.clicked.connect(self.save_all_settings)
        
        self.btn_reset = QPushButton("Restore Backup")
        self.btn_reset.setObjectName("BtnReset")
        self.btn_reset.clicked.connect(self.reset_ini_file)

        bottom_layout.addWidget(self.check_readonly)
        bottom_layout.addWidget(self.btn_save)
        bottom_layout.addWidget(self.btn_reset)
        main_layout.addLayout(bottom_layout)

    def _get_stylesheet(self):
        return """
            QWidget { background-color: #121212; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
            #PathCard { background-color: #1e1e1e; border-radius: 10px; padding: 10px; border: 1px solid #333; }
            #SettingCard { background-color: #1e1e1e; border-radius: 12px; padding: 15px; border: 1px solid #2a2a2a; }
            #SettingCard:hover { border: 1px solid #00d4ff; }
            QPushButton { background-color: #333; border-radius: 6px; padding: 8px 15px; font-weight: bold; }
            QPushButton:hover { background-color: #444; }
            #BtnSave { background-color: #0078d4; font-size: 12pt; letter-spacing: 1px; }
            #BtnSave:hover { background-color: #0086ed; }
            #BtnReset { background-color: #442222; border: 1px solid #662222; margin-top: 5px; }
            QSlider::handle:horizontal { background: #00d4ff; border-radius: 7px; width: 14px; height: 14px; margin: -5px 0; }
            QSlider::groove:horizontal { background: #333; height: 4px; border-radius: 2px; }
            QCheckBox { margin: 10px 0; }
            QScrollArea { background-color: transparent; }
        """

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
            self.load_file(potential_path)
            self.path_label.setText(f'File Location: {self.ini_file_path}')
            QMessageBox.information(
                self, 
                'HOORAY!!!', 
                'Engine.ini found and selected automatically! Ready to edit.'
            )
            self.refresh_ui_from_file()
        else:
            self.path_label.setText('File Location: Not Selected (Auto Detection Failed)')
            QMessageBox.warning(
                self, 
                'WHEREE!!!???', 
                'Engine.ini not found. Please select it manually.'
            )

    def manual_select_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Select Engine.ini', self.get_base_dir(), 'INI files (*.ini)')
        if fname: self.load_file(fname)

    def load_file(self, path):
        self.ini_file_path = path
        self.path_label.setText(f"Target: {path}")
        self.refresh_ui_from_file()

    def refresh_ui_from_file(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                pass

        current_values = {}
        if os.path.exists(self.ini_file_path):
            try:
                with open(self.ini_file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line and not line.startswith(';'):
                            k, v = line.split('=', 1)
                            current_values[k.strip()] = v.strip()
            except Exception as e:
                print(f"Error reading file: {e}")

        for key, config in SETTINGS_CONFIG.items():
            card = SettingCard(key, config, current_values.get(key))
            self.cards[key] = card
            self.scroll_layout.addWidget(card)
        
        self.scroll_layout.addStretch()

    def save_all_settings(self):
        if not self.ini_file_path: return
        
        try:
            ini_dir = os.path.dirname(self.ini_file_path)
            backup_dir = os.path.join(ini_dir, 'backup')
            os.makedirs(backup_dir, exist_ok=True)
            shutil.copyfile(self.ini_file_path, os.path.join(backup_dir, 'Engine_backup.ini'))
        except Exception as e:
            QMessageBox.warning(self, "Backup Error", str(e))

        try:
            current_mode = os.stat(self.ini_file_path).st_mode
            os.chmod(self.ini_file_path, current_mode | stat.S_IWRITE)

            with open(self.ini_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            new_data = {}
            for k, card in self.cards.items():
                new_data[k] = card.get_value()

            updated_lines = []
            found_keys = set()
            in_system = False
            
            for line in lines:
                clean = line.strip()
                if clean == '[SystemSettings]': in_system = True
                elif clean.startswith('[') and clean.endswith(']'): in_system = False
                
                key_match = False
                if in_system and '=' in clean:
                    k = clean.split('=')[0].strip()
                    if k in new_data:
                        updated_lines.append(f"{k}={new_data[k]}\n")
                        found_keys.add(k)
                        key_match = True
                
                if not key_match: updated_lines.append(line)

            if '[SystemSettings]\n' not in updated_lines and '[SystemSettings]' not in [l.strip() for l in updated_lines]:
                updated_lines.append("\n[SystemSettings]\n")
            
            sys_idx = -1
            for i, l in enumerate(updated_lines):
                if l.strip() == '[SystemSettings]':
                    sys_idx = i
                    break
            
            for k, v in new_data.items():
                if k not in found_keys:
                    updated_lines.insert(sys_idx + 1, f"{k}={v}\n")

            with open(self.ini_file_path, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)

            if self.check_readonly.isChecked():
                os.chmod(self.ini_file_path, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)

            QMessageBox.information(self, "Success", "All settings applied successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def reset_ini_file(self):
        if not self.ini_file_path: return
        backup = os.path.join(os.path.dirname(self.ini_file_path), 'backup', 'Engine_backup.ini')
        if os.path.exists(backup):
            os.chmod(self.ini_file_path, stat.S_IWRITE)
            shutil.copyfile(backup, self.ini_file_path)
            self.refresh_ui_from_file()
            QMessageBox.information(self, "Restored", "Backup restored!")

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    pyi_splash.close()
    app = QApplication(sys.argv)
    ex = ModernWavesEditor()
    ex.show()
    
    sys.exit(app.exec_())
