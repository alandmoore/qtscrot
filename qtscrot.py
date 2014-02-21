"""
QTScrot is a gui for the scrot screenshot utility.
Written by Alan D Moore, c 2014.
Written by Alan D Moore, c 2014.
Released under the GPL v. 3.0

Requires scrot and QT5.

"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from collections import namedtuple
from functools import partial
import subprocess
import sys
from shutil import which, copy
from datetime import datetime
import os

settingItem = namedtuple("settingItem", ["label", "args"])
preview_scale = .50

class ScrotGUI(QMainWindow):
    """The main GUI for the app"""

    def __init__(self, scrot_cmd):
        super(ScrotGUI, self).__init__()
        self.setWindowFlags(Qt.Dialog)
        self.scrot = scrot_cmd
        self.form = QWidget()
        self.formlayout = QVBoxLayout()
        self.form.setLayout(self.formlayout)
        self.setCentralWidget(self.form)
        self.command_args = []
        
        #ss display
        self.image_view = QLabel()
        self.formlayout.addWidget(self.image_view)
        screen = QApplication.desktop().availableGeometry()
        self.image_view_size = (screen.width() * preview_scale, screen.height() * preview_scale)
        self.image_view.setMaximumSize(*self.image_view_size)
        self.image_view.setSizePolicy(QSizePolicy(QSizePolicy.Maximum))
        
        #The execute button
        self.gobutton = QPushButton ("&Take Screenshot")
        self.gobutton.clicked.connect(self.take_screenshot)
        self.formlayout.addWidget(self.gobutton)
                
        #Type of shot
        self.shot_type_button_group = QButtonGroup()
        self.shot_types = [
            settingItem("&Full", ["-m"]),
            settingItem("&Current Screen", []),
            settingItem("Select &Window", ["-s", "-b"]),
            settingItem("Select W&indow (no border)", ["-s"])
            ]
        self.shot_type = self.shot_types[0]
        for i, shot_type in enumerate(self.shot_types):
            button = QRadioButton(shot_type.label)
            self.shot_type_button_group.addButton(button)
            self.formlayout.addWidget(button)
            button.toggled[bool].connect(partial(self.set_shot_type, i, shot_type.args))
            if i == 0:
                button.setChecked(True)

        # Countdown
        countdown_section = QWidget()
        countdown_section.setSizePolicy(QSizePolicy(QSizePolicy.Minimum))
        countdown_section.setLayout(QHBoxLayout())
        countdown_section.layout().addWidget(QLabel("Countdown"))
        self.countdown_time = QSpinBox()
        countdown_section.layout().addWidget(self.countdown_time)
        self.formlayout.addWidget(countdown_section)


        # Save button
        self.savebutton = QPushButton("Save Screenshot")
        self.savebutton.setShortcut(QKeySequence(QKeySequence.Save))
        self.savebutton.setEnabled(False)
        self.savebutton.clicked.connect(self.save_shot)
        self.formlayout.addWidget(self.savebutton)

        #Expander
        # expand the bottom so we don't look derpy
        self.expander = QWidget()
        self.expander.setSizePolicy(QSizePolicy(QSizePolicy.Expanding))
        self.formlayout.addWidget(self.expander)

        #show the app
        self.show()

    def set_shot_type(self, option_number, checked):
        if checked:
            self.shot_type = self.shot_types[option_number]


    def save_shot(self):
        save_filename = QFileDialog.getSaveFileName(None, "Screenshot Name", "", "Images (*.png)")
        copy(self.filename, save_filename[0])
        
    def take_screenshot(self):
        self.command_args = [self.scrot]
        self.command_args += self.shot_type.args
        countdown = self.countdown_time.value()
        if countdown > 0:
            self.command_args.append("-c")
            self.command_args.append("-d")
            self.command_args.append(countdown.__str__())
        else:
            if "-c" in self.command_args:
                self.command_args.remove("-c")
            if "-d" in self.command_args:
                ci = self.command_args.index("-d")
                del self.command_args[ci]
                if self.command_args[ci].isdigit():
                    del self.command_args[ci]
        self.filename = os.path.join("/tmp",
            datetime.now().strftime("qtscrot-%Y-%m-%d-%H%M%s%f.png"))
        self.command_args.append(self.filename)
        self.hide()
        print("Command executed: {}".format(" ".join(self.command_args)))
        subprocess.check_call(self.command_args)
        preview = QImage(self.filename).scaled(self.image_view_size[0], self.image_view_size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_view.setPixmap(QPixmap.fromImage(preview))
        self.savebutton.setEnabled(True)
        self.show()
        
if __name__ == '__main__':

    # check for existence of scrot
    scrot_cmd = which("scrot")
    if not scrot_cmd:
        sys.stderr.write("scrot was not found on your system.  Please install scrot to use this app.")
        sys.exit(1)
    app = QApplication(sys.argv)

    sg = ScrotGUI(scrot_cmd)
    app.exec_()
