# Author: Jacob Tsekrekos
# Date: Jun 13, 2018
# File: window.py
# Description: Main window class, does all back-end to get a console to act like a window
import subprocess as _subprocess

from ..enums import Colour as _Colour
from .setup import *
import time

logger.name = __name__
logger.setLevel(Logger.ERROR)

setup()

# implement a contant update (25 frames/second) that only affects graphics

class Window:
    def __init__(self, width, height):
        """
        Sets console's height and width based on the font size.
        Stores the width and height in order to draw later
        """
        self.font_dims = FONT_DIMS()

        self.width = None
        self.height = None

        # X: {Y: value)
        self.__coords = None
        self.resize(width, height)
        self.__background_tile = " "
        self.__background = None

    def fullScreen(self):
        """Takes the width and height of the screen in pixels and divides by the font dims to get a columns and rows.
        columns and rows are sent to the resize function"""
        dims = [i - j for i, j in zip(SCREEN_DIMS(), OFFSET())]
        self.resize(*dims)

    def resize(self, width, height):
        """ Sets the size of the console """
        cols = width // self.font_dims[0]
        lines = height // self.font_dims[1]
        # add in getstatusoutput to log errors more effectively?
        error = _subprocess.getoutput(CMD_SET_SIZE.format(cols, lines + 2))
        if error:
            logger.error(error)

        # Accounts for the indexing of the list starting at 0 and going to length - 1, width -1
        self.width, self.height = cols - 1, lines - 1
        self.__coords = {i: [] for i in range(self.height)}

    # FIXED?: Fix the random not showing character bug.
    def flush(self):
        """ Flushes the pixels to the screen. Does this by setting a default of the background_tile
        and goes through the list of all pixels and adds to the screen if it exists"""

        # Note a screen clear is not neccesary because each element in the current buffer is already being written to

        out = ""
        for y in range(self.height):
            row = self.__coords.get(y, [])

            line = ""
            # print(y, row)
            for x in range(self.width):
                if not row:
                    line += self.__background_tile
                elif row[0][0] == x:
                    line += _Colour.RESET + row[0][1]
                    row.pop(0)
                else:
                    line += self.__background_tile
            out += line + _Colour.RESET + "\n"
            self.__coords[y] = []
        print(_Colour.RESET + out + _Colour.RESET)

    @property
    def background(self):
        return self.__background

    @background.setter
    def background(self, colour):
        self.__background = colour
        self.__background_tile = colour + " " + _Colour.RESET

    def setPixel(self, x, y, value):
        if y not in range(0, self.height):
            return None
        for i, coord in enumerate(self.__coords[y]):
            if coord[0] > x:
                self.__coords[y].insert(i, (x, value))
                break
            elif coord[0] == x:
                self.__coords[y][i] = (x, value)
                break
        else:
            self.__coords[y].append((x, value))

    def pushMatrix(self, matrix, x=0, y=0):
        """
        :param x: x offset
        :param y: y offset
        :type matrix: Matrix
        :returns: None
        """
        for i in range(matrix.rows):
            for j in range(matrix.columns):
                self.setPixel(i + x, j + y, matrix[i][j])

    def addText(self, x, y, text):
        for letter in text:
            self.setPixel(x, y, letter)

    @staticmethod
    def SetLogLevel(enum):
        try:
            logger.setLevel(enum)
            return True
        except:
            return False


if __name__ == "__main__":
    w = Window(400, 400)
    w.fullScreen()
    w.setPixel(0, 0, "^")
    w.setPixel(w.width, w.height, "$")
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
