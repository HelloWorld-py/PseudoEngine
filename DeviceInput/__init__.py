# Author: Jacob Tsekrekos
# Date: Jun 1, 2018
# File: DeviceInput.__init__.py
# Description: Init for the DeviceInput module

from pynput import keyboard as _keyboard
from pynput import mouse as _mouse
from .Gamepad import get_gamepad as _get_gamepad
from .Gamepad import check_gamepad as _check_gamepad
from .Gamepad import UnpluggedError as _UnpluggedError
from .IndexCodes import ButtonCode, KeyCode, XCode
from threading import Thread as _Thread
# Gamepad is a stripped down inputs.py (mouse and keyboard handlers were not working)


# todo fix 2d checking (ACCESS)
class UpdateChecker:
    def __init__(self):
        self.__vals = {}
        self.__updated = set()

    def __setitem__(self, key, value):
        self.__vals[key] = value
        self.__updated.add(key)

    def __getitem__(self, item):
        if self.__updated.__contains__(item):
            self.__updated.remove(item)
        return self.__vals.get(item)

    def __str__(self):
        return str(self.__vals)

    def keys(self):
        return [key for key in self.__vals.keys()]

    @property
    def update_list(self):
        return list(self.__updated)

    @property
    def has_updated(self):
        return len(self.__updated) > 0


keys = UpdateChecker()
mouse = UpdateChecker()
gamepad = UpdateChecker()


def keyboard_handler(callback=None):
    """
    :returns an input thread
    Call keyboard_handler.start() in order to start listening
    """
    if callback is None:
        def callback():
            pass

    # key handler functions
    def on_press(key):
        keys[KeyCode.code_of(key)] = True
        callback()

    def on_release(key):
        keys[KeyCode.code_of(key)] = False
        callback()

    def get_input():
        with _keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

    return _Thread(target=get_input, name="Keyboard-Thread", daemon=True)


def mouse_handler(callback=None):
    """
    :returns an input thread
    Call mouse_handler.start() in order to start listening
    """
    if callback is None:
        def callback():
            pass

    def on_move(x, y):
        mouse["Pos"] = (x, y)
        callback()

    def on_click(x, y, button, pressed):
        mouse[ButtonCode.code_of(button)] = pressed
        callback()

    def on_scroll(x, y, dx, dy):
        mouse["HScroll"] = dx
        mouse["VScroll"] = dy
        callback()

    # Collect events until released
    def get_input():
        with _mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
            listener.join()

    return _Thread(target=get_input, name="Mouse-Thread", daemon=True)


def gamepad_handler(callback=None):
    """
    :returns an input thread
    Call keyboard_handler.start() in order to start listening
    *NOTE* IF THERE IS NO CONTROLLER FOUND, the thread will exit
    """
    if callback is None:
        def callback():
            pass

    gamepad[XCode.DPAD0] = [0, 0]
    gamepad[XCode.DPAD1] = [0, 0]
    gamepad[XCode.DPAD2] = [0, 0]
    gamepad[XCode.DPAD3] = [0, 0]

    # STICKS ARE BUGGED!!
    gamepad[XCode.LSTICK] = [0, 0]
    gamepad[XCode.RSTICK] = [0, 0]

    if not _check_gamepad():
        e = True
        # todo: log that the gamepad thread will exit?

    def get_input():
        if e:
            print("No gamepad found")
            exit(-1)

        while True:
            events = _get_gamepad()

            for event in events:
                index = XCode.code_of(event.code)
                if event.ev_type == "Sync":
                    continue
                if event.code[-1] == "X":
                    gamepad[index][0] = event.state
                elif event.code[-1] == "Y":
                    gamepad[index][1] = event.state
                else:
                    gamepad[index] = event.state

                callback()
                # if event.ev_type == "Absolute":
                #     callback()
                #
                # elif event.ev_type == "Key":
                #     if event.state == 1:
                #         callback()
                #     elif event.state == 0:
                #         callback()

    return _Thread(target=get_input, name="Gamepad-Thread", daemon=True)