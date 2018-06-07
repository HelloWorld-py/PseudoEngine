# 2018/04/20
# todo: Add Documentation

from pynput import mouse as _mouse
import re as _re

# todo implement re?


class KeyCode:
    """KeyCode Class allows for an abstraction between the listeners and the window class.
    When queried, this class will return"""
    # !!!NOTE THESE NAMES ARE TIED CLOSELY WITH pynput'S VARIABLE NAMES!!!
    # Letters key codes are ascii values
    CMD = 0
    PAUSE = 1
    PAGE_UP = 2
    PAGE_DOWN = 3
    END = 4
    HOME = 5
    BACKSPACE = 8
    TAB = 9
    PRINT_SCREEN = 10
    ENTER = 11
    CTRL = 12
    ALT = 13
    SHIFT = 14
    MENU = 15
    NUM = 17
    CAPS = 18
    SCROLL = 19
    INSERT = 26
    ESC = 27
    LEFT = 28
    UP = 29
    RIGHT = 30
    DOWN = 31
    SPACE = 32
    F1 = 101
    F2 = 102
    F3 = 103
    F4 = 104
    F5 = 105
    F6 = 106
    F7 = 107
    F8 = 108
    F9 = 109
    F10 = 110
    F11 = 111
    F12 = 112
    DELETE = 127

    @staticmethod
    def __getitem__(self, key):
        return KeyCode.code_of(key)

    @staticmethod
    def code_of(key):
        if isinstance(key, str):
            key = key.upper()
            if len(key) == 1:
                return ord(key)
            return vars(KeyCode).get(key, None)
        else:
            try:
                return ord(key.char.upper())
            except AttributeError:
                k = (str(key)[4:]).upper()
                k = k[:-2] if k[-2:] in ["_L", "_R"] else k
                k = k[:-5] if k[-5:] == "LOCK" else k
                return vars(KeyCode).get(k, None)


class ButtonCode:
    LEFT = 0
    RIGHT = 1
    MIDDLE = 2

    __special = {
        _mouse.Button.left.value: LEFT,
        _mouse.Button.right.value: RIGHT,
        _mouse.Button.middle.value: MIDDLE
    }

    @staticmethod
    def code_of(button):
        if isinstance(button, str):
            return vars(ButtonCode).get(button, None)
        else:
            return ButtonCode.__special.get(button.value, None)


class XCode:
    START = "START"
    SELECT = "SELECT"
    NORTH = "N"
    EAST = "E"
    SOUTH = "S"
    WEST = "W"
    LB = "LB"
    RB = "RB"
    LTHUMB = "LTHUMB"
    RTHUMB = "RTHUMB"
    LT = "LT"
    RT = "RT"
    DPAD0 = "D0"
    DPAD1 = "D1"
    DPAD2 = "D2"
    DPAD3 = "D3"
    LSTICK = "LSTICK"
    RSTICK = "RSTICK"

    __special = {
        "TL": "LB",
        "TR": "RB",
        "THUMBL": "LTHUMB",
        "THUMBR": "RTHUMB",
        "LZ": "LT",
        "RZ": "RT",
        "LX": "LSTICK",
        "LY": "LSTICK",
        "RX": "RSTICK",
        "RY": "RSTICK",
        "DPAD0X": "DPAD0",
        "DPAD0Y": "DPAD0",
        "DPAD1X": "DPAD1",
        "DPAD1Y": "DPAD1",
        "DPAD2X": "DPAD2",
        "DPAD2Y": "DPAD2",
        "DPAD3X": "DPAD3",
        "DPAD3Y": "DPAD3",
    }

    @staticmethod
    def code_of(button):
        button = button[4:]
        button = XCode.__special[button] if XCode.__special.get(button, False) else button
        return vars(XCode).get(button, None)


if __name__ == "__main__":
    pass