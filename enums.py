# Author: Jacob Tsekrekos
# Date: Jun 1, 2018
# File: enums.py
# Description: Holds all enums for the Engine.


class Logging:
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


# http://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html
# todo add RGB/RGBA Translation
class Colour:

    FOREGROUND = "38;5;"
    BACKGROUND = "48;5;"

    B_BLACK = "\u001b[40m"
    B_RED = "\u001b[41m"
    B_GREEN = "\u001b[42m"
    B_YELLOW = "\u001b[43m"
    B_BLUE = "\u001b[44m"
    B_MAGENTA = "\u001b[45m"
    B_CYAN = "\u001b[46m"
    B_WHITE = "\u001b[47m"
    NORMAL = ""
    BRIGHT = ";1m"

    RESET = "\u001b[0m"


    @staticmethod
    def join(place, colour):
        return "\u001b[{}{}m".format(place, colour)


if __name__ == "__main__":
    print(Colour.B_CYAN + Colour.join(Colour.FOREGROUND, 34) + "ABC" + Colour.RESET)

