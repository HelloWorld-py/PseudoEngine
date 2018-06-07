import logging as _logging
import os as _os
import platform as _platform
import re as _re
import subprocess as _subprocess
import time as _time

from Prototyping.matrix import *

logger = _logging.getLogger(__name__)

logger.setLevel(_logging.DEBUG)

file_handler = _logging.FileHandler("./graphics.log")
file_handler.setFormatter(_logging.Formatter("%(asctime)s|[%(levelname)s] %(message)s"))


# todo add stream handler when able to open another console
# stream_handler = _logging.StreamHandler()
logger.addHandler(file_handler)
# logger.addHandler(stream_handler)

_os.system("")
_system = _platform.system()
logger.info(_system)
if _system == "Windows":
    _MONITOR_DIMS = "wmic path Win32_VideoController get CurrentHorizontalResolution^,CurrentVerticalResolution /format:Value"
    _FONT_DIMS = "REG QUERY HKEY_CURRENT_USER\Console /v FontSize"
    _FONT_FACE = "REG QUERY HKEY_CURRENT_USER\Console /v FaceName"
    _DEFAULT_POS = "REG QUERY HKEY_CURRENT_USER\Console /v WindowPosition"
    _SET_SIZE = "mode con: cols={} lines={}"
    _RE_HOR_REZ = _re.compile("(?<=HorizontalResolution=)\d{3,4}")
    _RE_VER_REZ = _re.compile("(?<=VerticalResolution=)\d{3,4}")
    _RE_FACE_NAME = _re.compile("(?<=REG_SZ\s{4})[\w ]+")

    def _NO_OUTPUT():
        _os.system("@echo off")

    def CLEAR():
        _os.system("cls")

    def PAUSE():
        _os.system("pause > nul")

    # TEST IF ABLE TO USE REG QUERY
    if _subprocess.getstatusoutput(_FONT_DIMS)[0] != 0:
        logger.error("Cannot read registry(REG QUERY): USING DEFAULTS")
        _REG_READABLE = False
    else:
        _REG_READABLE = True
else:
    logger.critical("Platform ({}) is not yet supported".format(_system))
    _REG_READABLE = False
    exit(-1)

_RE_HEX = _re.compile(r"\b0x[\da-fA-F]+\b")


class Window:
    def __init__(self, width, height):
        _NO_OUTPUT()
        self.font_dims = Window.__get_font_info()

        self.width = None
        self.height = None

        self.__pixels = None
        self.resize(width, height)

    def fullScreen(self):
        screen_dims = Window.__get_monitor_dims()
        # WHY IS THERE OFFSET?
        offset = [10, 75]
        # OFFSET CAUSED BECAUSE OF THE WINDOW HEADER <- take screen pos into consideration
        # offset = [0, 65]
        dims = [i - j for i, j in zip(screen_dims, offset)]
        self.resize(*dims)

    def resize(self, width, height):
        cols = width // self.font_dims[0]
        lines = height // self.font_dims[1]
        error = _subprocess.getoutput(_SET_SIZE.format(cols, lines + 2))
        if error:
            logger.warning(error)

        if self.__pixels:
            del self.__pixels
        self.__pixels = Matrix(cols, lines)

        # Accounts for the indexing of the list starting at 0 and going to length - 1, width -1
        self.width, self.height = cols - 1, lines - 1
        # return cols, lines

    def setPixel(self, x, y, value):
        self.__pixels[x][y] = value

    def flush(self):
        e = [[str(j) for j in i] for i in zip(*self.__pixels.elements)]
        CLEAR()
        print("\n".join("".join(i) for i in e))

    def addText(self, x, y, text):
        for letter in text:
            self.setPixel(x, y, letter)

    def setBackground(self, colourENUM):
        pass

    @staticmethod
    def __get_monitor_dims():
        command = _MONITOR_DIMS
        raw_dims = _subprocess.getoutput(command)
        res_hor = int(_re.search(_RE_HOR_REZ, raw_dims).group())
        res_ver = int(_re.search(_RE_VER_REZ, raw_dims).group())
        logger.debug("Monitor is {} x {}".format(res_hor, res_ver))
        return res_hor, res_ver

    @staticmethod
    def __get_font_info():
        # font_height only uses 4 upper bits for ttf fonts
        if _REG_READABLE:
            raw_font_height = _subprocess.getoutput(_FONT_DIMS)
            font_height = int("0x{:08X}".format(int(_re.search(_RE_HEX, raw_font_height).group(), 16))[:-4], 16)
            font_width = font_height // 2

            raw_face_name = _subprocess.getoutput(_FONT_FACE)
            face_name = _re.search(_RE_FACE_NAME, raw_face_name).group()
            # raw_font_family = _re.search(_RE_HEX, raw_face_name).group()
        else:
            font_width, font_height, face_name = 8, 16, "Consolas"

        logger.debug("Font size: {}x{}".format(font_width, font_height))
        return font_width, font_height, face_name

    @staticmethod
    def __get_default_position():
        # upper 4 digits used for top, lower 4 digits used for left
        if not _REG_READABLE:
            return 0, 0

        raw_pos = _subprocess.getoutput(_DEFAULT_POS)
        pos = "{:08X}".format(int(_re.search(_RE_HEX, raw_pos).group(), 16))
        top = int(pos[:-4], 16)
        left = int(pos[-4:], 16)

        if top > 65530:
            top = -(65536 - top)
        if left > 65530:
            left = -(65536 - left)

        return top, left

    @staticmethod
    def SetLogLevel(enum):
        try:
            logger.setLevel(enum)
            return True
        except:
            return False


# todo: add a tranformation matrices to allow for pixel values to be stored?

if __name__ == "__main__":
    w = Window(400, 400)
    w.fullScreen()
    w.setPixel(0, 0, "^")
    w.setPixel(w.width, w.height,"$")
    w.flush()
    i = 1
    j = 0

    while True:
        w.setPixel(i, j, "+")
        w.flush()
        w.setPixel(i, j, " ")
        i += 2
        if i > w.width:
            i = 0
            j += 2
        if j > w.height:
            break
        _time.sleep(1/60)