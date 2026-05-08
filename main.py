import PyQt5.QtWidgets
import PyQt5.QtGui
from PyQt5 import uic
import sys

from matchmaker import Game as MatchmakerGame
import webbrowser

rnc_style = ""
with open("uisrc\\rnc_style.qss", "r") as file:
    rnc_style = file.read()

base_style = ""
with open("uisrc\\base_style.qss", "r") as file:
    base_style = file.read()

class Window(PyQt5.QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__()

        uic.loadUi("uisrc/test.ui", self)

        self.matchmaker_game = MatchmakerGame(0.2, 0.6)
        self.matchmaker_game.new_round()
        self.mmk_percent = self.findChild(PyQt5.QtWidgets.QLabel, "mmk_percent")
        self.mmk_win_count = self.findChild(PyQt5.QtWidgets.QLabel, "mmk_win_count")
        self.mmk_total_count = self.findChild(PyQt5.QtWidgets.QLabel, "mmk_total_count")
        self.mmk_a1 = self.findChild(PyQt5.QtWidgets.QLabel, "mmk_a1")
        self.mmk_a2 = self.findChild(PyQt5.QtWidgets.QLabel, "mmk_a2")

        self.mmk_update()

        logo_label: PyQt5.QtWidgets.QLabel = self.findChild(PyQt5.QtWidgets.QLabel, "logo_label")
        logo_label.setPixmap(PyQt5.QtGui.QPixmap("uisrc\\Finder.png"))

        stack_widget: PyQt5.QtWidgets.QStackedLayout = self.findChild(PyQt5.QtWidgets.QStackedWidget)
        # Start past menu screen ( dont need :[ )
        stack_widget.setCurrentIndex(1)

        self.index_trail = []

        # Quickly assigning buttons by name

        self.buttons_data = [
            [
                # Button ID
                "matchmaker_button",
                # Base image, RNC image
                ("uisrc\\Matchmaker Menu.png", "uisrc\\Matchmaker Menu.png"),
                # Callback
                lambda: self.set_index(stack_widget, 1)
            ],
            [
                "menu_back",
                ("uisrc\\Arrow.png", "uisrc\\RNC Arrow.png"),
                lambda: self.prev_index(stack_widget)
            ]
        ] +\
        [
            [
                f"mmk_menu_start_{n}",
                ("", ""),
                lambda: self.set_index(stack_widget, 2)
            ]
            for n in range(12)
        ] +\
        [
            [
                "mmk_good",
                ("uisrc\\Heart Button.png", "uisrc\\RNC Heart Button.png"),
                lambda: self.mmk_command("good")
            ],
            [
                "mmk_bad",
                ("uisrc\\X Button.png", "uisrc\\RNC X Button.png"),
                lambda: self.mmk_command("bad")
            ],
            [
                "mmk_skip",
                ("uisrc\\Skip Button.png", "uisrc\\RNC Skip Button.png"),
                lambda: self.mmk_command("skip")
            ],
            [
                "mmk_help",
                ("uisrc\\Info Question Button.png", "uisrc\\RNC Info Question Button.png"),
                lambda: self.mmk_command("help")
            ]
        ]

        for bttn in self.buttons_data:
            mbutton: PyQt5.QtWidgets.QPushButton = self.findChild(PyQt5.QtWidgets.QPushButton, bttn[0])
            mbutton.clicked.connect(bttn[2])

            if mbutton.objectName().find("mmk_menu_start_") == 0:
                bttn_text = mbutton.text()
                bttn_with_idx = bttn_text.find("with ")
                if bttn_with_idx == -1:
                    bttn_with_idx = bttn_text.rfind(' ') + 1
                else:
                    bttn_with_idx += len("with ")
                bttn_ref = bttn_text[bttn_with_idx:]
                icon_name = "uisrc\\icons\\" + bttn_ref + ".png"
                bttn[1] = (icon_name, icon_name)
                print(icon_name)

            bttn[0] = mbutton

        matchmaker_theme_check: PyQt5.QtWidgets.QCheckBox = None
        matchmaker_theme_check = self.findChild(PyQt5.QtWidgets.QCheckBox, "matchmaker_theme_check")

        matchmaker_theme_check.clicked.connect(self.set_rnc_theme)

        self.set_rnc_theme(False)
    
    def set_index(self, widget: PyQt5.QtWidgets.QStackedLayout, idx):
        self.index_trail.append(widget.currentIndex())
        widget.setCurrentIndex(idx)
    
    def prev_index(self, widget: PyQt5.QtWidgets.QStackedLayout):
        if len(self.index_trail) == 0:
            return
        
        idx = self.index_trail.pop()
        widget.setCurrentIndex(idx)
    
    def set_rnc_theme(self, set):
        if set:
            self.setStyleSheet(rnc_style)
        else:
            self.setStyleSheet(base_style)

        for bttn in self.buttons_data:
            idx = 1 if set else 0

            widget: PyQt5.QtWidgets.QPushButton = bttn[0]
            widget.setIcon(PyQt5.QtGui.QIcon(PyQt5.QtGui.QPixmap(bttn[1][idx])))
    
    def mmk_update(self):
        self.mmk_percent.setText(f"{int(self.matchmaker_game.min_similarity * 100)}%")
        self.mmk_win_count.setText(f"{(self.matchmaker_game.correct_guesses)}")
        self.mmk_total_count.setText(f"{(self.matchmaker_game.total_guesses)}")
        self.mmk_a1.setText(self.matchmaker_game.a1[0])
        self.mmk_a2.setText(self.matchmaker_game.a2[0])

    def mmk_command(self, command):
        print("MMK: COMMAND " + command)
        
        match command:
            case "good":
                self.matchmaker_game.cmd_good()
            case "bad":
                self.matchmaker_game.cmd_bad()
            case "skip":
                self.matchmaker_game.cmd_skip()
            case "help":
                webbrowser.open_new_tab(self.matchmaker_game.client.host + self.matchmaker_game.a1[1])
                webbrowser.open_new_tab(self.matchmaker_game.client.host + self.matchmaker_game.a2[1])

        self.mmk_update()

app = PyQt5.QtWidgets.QApplication(sys.argv)
window = Window()
window.show()
app.exec()
