import sys
import requests
import json
import time
import threading
import asyncio
import httpx


from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5 import uic

URL = "http://127.0.0.1:8000"

i = 0


class MyGUI(QMainWindow):
    def __init__(self):
        super(MyGUI, self).__init__()
        uic.loadUi("testui12.ui", self)
        self.show()
        self.timer = {"h": 0, "m": 0, "s": 0}
        self.menu_show = False
        self.current_activity = None

        # Page 1
        self.page_1_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_1))
        # Page 2
        self.page_2_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_4))

        # Home Page
        self.HomeButton.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_3))
        self.HomeButton.clicked.connect(self.hide_menu)
        self.HomeButton.clicked.connect(self.stop_timer)
        self.HomeButton.clicked.connect(lambda: self.save_activity(self.current_activity))

        # Create Page
        self.create_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.create_page))

        # Create New Activity
        self.confirm_create_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_1))
        self.confirm_create_button.clicked.connect(self.show_menu)
        self.confirm_create_button.clicked.connect(self.create_activity)

        # Inside Create Page
        self.go_back_create_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_3))

        # Continue button
        self.continue_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.continue_page))
        self.continue_button.clicked.connect(self.load_save)
        self.go_back_continue_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_3))

        # Double Click Continue item
        self.listWidget.itemDoubleClicked.connect(self.load_activity)
        self.listWidget.itemDoubleClicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_1))
        # Timer Count
        self.count = 0
        self.minute = 0
        self.hour = 0

        # Hide Menu on Start
        self.frame_left_menu.setHidden(True)

        # Create timer object
        self.Qtimer = QtCore.QTimer(self)
        self.Qtimer.timeout.connect(self.start_time)
        self.Qtimer.start(100)

        # Timer start
        self.start = False
        self.startButton.clicked.connect(self.start_timer)

        # Timer stop
        self.stopButton.clicked.connect(lambda: self.save_activity(self.current_activity))
        self.stopButton.clicked.connect(self.stop_timer)

        # Edit Button
        self.edit_button.clicked.connect(self.edit_time)

    def edit_time(self):
        pass

    def load_save(self):
        self.listWidget.clear()
        with open("save.json", "r") as openfile:
            dict_object = json.load(openfile)
        print(dict_object)

        for x,y in dict_object.items():
            activity_string = str(x) + " | " + "Level " + str(dict_object[x]["level"]) + " | " + "Time: " + str(dict_object[x]["time"]["h"]) + ":" + str(dict_object[x]["time"]["m"]) + ":" + str(dict_object[x]["time"]["s"])[:2] + " s"
            self.listWidget.addItem(activity_string)

    def load_activity(self):

        text = self.listWidget.currentItem().text()
        spl_char = " |"

        ind = text.find(spl_char)
        res = text[0:ind]

        with open("save.json", "r") as openfile:
            dict_object = json.load(openfile)

        activity_time = {}
        activity_time["h"] = dict_object[res]["time"]["h"]
        activity_time["m"] = dict_object[res]["time"]["m"]
        activity_time["s"] = dict_object[res]["time"]["s"]

        activity_name = res
        activity_level = int(dict_object[res]["level"])
        activity_xp = int(dict_object[res]["xp"])

        loaded_activity = Activity(activity_name, activity_time, activity_level, activity_xp)

        text = str(loaded_activity.total_time['s'] / 10) + " s"
        minute_text = str(loaded_activity.total_time['m']) + " M"

        self.TimerLabel.setText(text)
        self.MinuteLabel.setText(minute_text)
        self.set_current_activity(loaded_activity)
        self.show_menu()


    def create_activity(self):
        """
        Creates a new activity object
        """
        activity_name = self.activity_name_input.text()
        new_activity = Activity(activity_name)
        self.activity_name_input.setText("")
        self.set_current_activity(new_activity)
        self.reset_time()
        self.save_activity(new_activity)

    def set_current_activity(self, activity):
        """
        Sets the timer labels and function to the inputted activity
        """
        if self.current_activity is not None:
            self.save_activity(self.current_activity)

        self.current_activity = activity

        self.current_activity_label.setText(activity.activity_name)
        self.current_level_label.setText("Current Level: " + str(activity.current_level))

        self.minute = activity.total_time['m']
        self.hour = activity.total_time['h']
        self.count = activity.total_time['s']

    def hide_menu(self):
        """
        Hides the Left Menu
        """
        self.frame_left_menu.setHidden(True)

    def show_menu(self):
        """
        Shows the Left Menu
        """
        self.frame_left_menu.setHidden(False)

    def save_activity(self, activity=None):

        if activity is None:
            activity = self.current_activity
        with open("save.json", "r") as openfile:
            json_object = json.load(openfile)

        save_object = {
            "time": activity.total_time,
            "level": activity.current_level,
            "xp": activity.current_xp
        }

        json_object[activity.activity_name] = save_object

        save_json = json.dumps(json_object, indent=4)

        with open("save.json", "w") as outfile:
            outfile.write(save_json)

    def start_timer(self):
        self.start = True

    def stop_timer(self):
        self.start = False

    def reset_time(self):
        """
        Resets the timer labels to default numbers
        """
        self.TimerLabel.setText("0.0 s")
        self.MinuteLabel.setText("0 M")
        self.HourLabel.setText("0 H")

    def start_time(self):
        # time_request = httpx.post("http://127.0.0.1:8000/timer", data='{"h":0, "m":0, "s":0}')
        #
        # #  time_request = requests.post(url=URL + "/timer", json=self.timer)
        # print(time_request.json())

        # checking if flag is true
        if self.start:
            # incrementing the counter
            self.current_activity.total_time['s'] += 1

            if self.current_activity.total_time['s'] == 600:
                self.current_activity.total_time['s'] = 0
                self.current_activity.total_time['m'] += 1
                self.progressBar.setValue(self.minute * 10)

        if self.start:
            # getting text from count
            text = str(self.current_activity.total_time['s'] / 10) + " s"
            minute_text = str(self.current_activity.total_time['m'])

            # showing text
            self.TimerLabel.setText(text)
            self.MinuteLabel.setText(minute_text + " M")

    async def sendText(self):
        print(self.testText.toPlainText())
        myobj = {"text": self.testText.toPlainText()}
        p = requests.post(url=URL, json=myobj)
        print("p", p.json())

    def updateText(self):
        myobj = {"name": self.testText.toPlainText()}
        p = requests.put(url="http://127.0.0.1:8000/name", json=myobj)


class Activity:
    def __init__(self, activity_name, total_time=None, current_level=None, current_xp=None):
        if total_time is None:
            total_time = {"h": 0, "m": 0, "s": 0}
        if current_level is None:
            current_level = 1
        if current_xp is None:
            current_xp = 0
        self.activity_name = activity_name
        self.total_time = total_time
        self.current_level = current_level
        self.current_xp = current_xp

    def update_time(self, hour, minute, second):
        self.total_time["h"] = hour
        self.total_time["m"] = minute
        self.total_time["s"] = second


def main():
    app = QApplication([])
    window = MyGUI()
    app.exec_()


if __name__ == "__main__":
    main()
