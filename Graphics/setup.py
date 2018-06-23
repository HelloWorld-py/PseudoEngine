# Author: Jacob Tsekrekos
# Date: Jun 19, 2018
# File: setup.py
# Description: Gets all required information to allow the game engine to run. Call setup in the window class to get all
# information

from ..utils.logger import Logger as _Logger
from ..enums import Logging as _LoggingEnums
import re as _re
import os as _os
import platform as _platform
import subprocess as _subprocess

logger = _Logger(__name__, _LoggingEnums.ERROR, "graphics.log")

# Defaults and variable declaration for use in window.py
FONT_FACE = "Consolas"
FONT_DIMS = 8, 16
SCREEN_DIMS = None
DEFAULT_POSITION = 0, 0
OFFSET = 0, 0
CMD_SET_SIZE = None

SYSTEM = _platform.system()

_RE_HEX = _re.compile(r"\b0x[\da-fA-F]+\b")
_reg_readable = None


def CLEAR():
    pass


def PAUSE():
    pass


# Allows for colours to be used (for some reason...)
_os.system("")

_version = _re.search(r"^\d+", _platform.version())
_version = _version.group() if _version else False

if SYSTEM == "Windows":
    logger.info(SYSTEM)
    # No Output
    _os.system("@echo off")

    _CMD_MONITOR_DIMS = "wmic path Win32_VideoController get CurrentHorizontalResolution^,CurrentVerticalResolution /format:Value"
    _CMD_FONT_DIMS = "REG QUERY HKEY_CURRENT_USER\Console /v FontSize"
    _CMD_FONT_FACE = "REG QUERY HKEY_CURRENT_USER\Console /v FaceName"
    _CMD_DEFAULT_POS = "REG QUERY HKEY_CURRENT_USER\Console /v WindowPosition"
    CMD_SET_SIZE = "mode con: cols={} lines={}"
    _RE_HOR_REZ = _re.compile("(?<=HorizontalResolution=)\d{3,4}")
    _RE_VER_REZ = _re.compile("(?<=VerticalResolution=)\d{3,4}")
    _RE_FACE_NAME = _re.compile("(?<=REG_SZ\s{4})[\w ]+")


    def CLEAR():
        _os.system("cls")


    def PAUSE():
        _os.system("pause > nul")


    if _version == "10":
        OFFSET = 10, 75

    elif _version == "7":
        OFFSET = 0, 65
else:
    # For other platforms, ensure a command that stops output is called
    # Below code is technically superfluous but it stops the IDE from getting confused
    _CMD_MONITOR_DIMS = None
    _CMD_FONT_DIMS = None
    _CMD_FONT_FACE = None
    _CMD_DEFAULT_POS = None
    _CMD_SET_SIZE = None
    _RE_HOR_REZ = None
    _RE_VER_REZ = None
    _RE_FACE_NAME = None
    logger.critical("Platform ({}) is not yet supported".format(SYSTEM))
    exit(-1)


def _get_font_info():
    global FONT_DIMS, FONT_FACE

    # font_height only uses 4 upper bits for ttf fonts
    if _reg_readable:
        raw_font_height = _subprocess.getoutput(_CMD_FONT_DIMS)
        font_height = int("0x{:08X}".format(int(_re.search(_RE_HEX, raw_font_height).group(), 16))[:-4], 16)
        font_width = font_height // 2

        raw_face_name = _subprocess.getoutput(_CMD_FONT_FACE)
        face_name = _re.search(_RE_FACE_NAME, raw_face_name).group()
        # raw_font_family = _re.search(_RE_HEX, raw_face_name).group()
    else:
        font_width, font_height, face_name = 8, 16, "Consolas"

    logger.debug("Font size: {}x{}".format(font_width, font_height))

    FONT_DIMS = font_width, font_height
    FONT_FACE = face_name


def _get_default_position():
    global DEFAULT_POSITION
    # upper 4 digits used for top, lower 4 digits used for left
    if not _reg_readable:
        return 0, 0

    raw_pos = _subprocess.getoutput(_CMD_DEFAULT_POS)
    pos = "{:08X}".format(int(_re.search(_RE_HEX, raw_pos).group(), 16))
    top = int(pos[:-4], 16)
    left = int(pos[-4:], 16)

    if top > 65530:
        top = -(65536 - top)
    if left > 65530:
        left = -(65536 - left)

    return top, left


def __screen_dims_mouse():
    from ..DeviceInput import mouse_handler as _mouse_handler
    from ..DeviceInput import mouse as _mouse
    from ..DeviceInput import ButtonCode as _ButtonCode
    ex = False

    def end():
        nonlocal ex
        if _mouse[_ButtonCode.RIGHT]:
            ex = True

    _mouse_handler(end).start()

    maxPos = [0, 0]

    while True:
        print("Right Click to exit.")
        print(maxPos)
        _os.system("cls")

        a = _mouse["pos"]
        if not a:
            continue

        if a[0] > maxPos[0] and a[0] % 16 == 0:
            maxPos[0] = a[0]

        if a[1] > maxPos[1] and a[1] % 9 == 0:
            maxPos[1] = a[1]

        if ex:
            break

    return maxPos if (maxPos[0] // 16 * 9 == maxPos[1]) else [maxPos[0] - 80, maxPos[1] - 80]


def __screen_dims_manual():
    while True:
        a = input("Screen Dimensions (l x h): ")
        try:
            return list(map(int, a.split(" x ")))
        except:
            print("Invalid input: Incorrect format. Try again")
            continue


def __screen_dims_auto():
    __status, raw_dims = _subprocess.getstatusoutput(_CMD_MONITOR_DIMS)
    if __status != 0:
        logger.error("WMIC command failed. Getting settings from manual input")
        print("Could not automatically set the screen size.")
        return False
    else:
        res_hor = int(_re.search(_RE_HOR_REZ, raw_dims).group())
        res_ver = int(_re.search(_RE_VER_REZ, raw_dims).group())
        logger.debug("Monitor is {} x {}".format(res_hor, res_ver))
        screen_dims = res_hor, res_ver
        return screen_dims


def _get_screen_info():
    global SCREEN_DIMS

    screen_dims = __screen_dims_auto()
    if not screen_dims:
        while True:
            print("(1)Type screen dimensions or (2)find them with the _mouse? (1 or 2) ")
            try:
                choice = int(input(""))
                if choice not in [1, 2]:
                    raise TypeError()
                break
            except:
                print("Invalid input. Try again")

        if choice == 1:
            screen_dims = __screen_dims_manual()
        else:
            screen_dims = __screen_dims_mouse()

    SCREEN_DIMS = screen_dims


def setup():
    global _reg_readable
    if _subprocess.getstatusoutput(_CMD_FONT_DIMS)[0] != 0:
        logger.error("Cannot read registry(REG QUERY): USING DEFAULTS")
        print("Please change your default font to be Consolas 16 (or another 8 x 16 font)")
        input("Press enter to continue...")
        _reg_readable = False
    else:
        _reg_readable = True

    # Functions set the global variables inside
    _get_screen_info()
    _get_font_info()
    _get_default_position()
