# Author: Jacob Tsekrekos
# Date: Jun 19, 2018
# File: setup.py
# Description: sets up the window dimensions to be used by the window class if REGEDIT is restricted or
# WMIC doesn't exist
from ..DeviceInput import mouse_handler as _mouse_handler
from ..DeviceInput import mouse as _mouse
from ..DeviceInput import ButtonCode as _ButtonCode

from ..engine_math import infinity as _infinity
from os import system as __system

screen_dims = [_infinity, _infinity]


def screen_dims_auto():
    global screen_dims
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
        __system("cls")

        a = _mouse["pos"]
        if not a:
            continue

        if a[0] > maxPos[0] and a[0] % 16 == 0:
            maxPos[0] = a[0]

        if a[1] > maxPos[1] and a[1] % 9 == 0:
            maxPos[1] = a[1]

        if ex == True:
            break

    screen_dims = maxPos if (maxPos[0] // 16 * 9 == maxPos[1]) else [maxPos[0] - 80, maxPos[1] - 80]


def screen_dims_manual():
    global screen_dims
    while True:
        a = input("Screen Dimensions (l x h): ")
        try:
            screen_dims = list(map(int, a.split(" x ")))
            break
        except:
            print("Invalid input: Not a Number. Try again")
            continue


def run():
    print("Please change your default font to be Consolas 16 (or another 8 x 16 font)")
    input("Ready? ")

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
        screen_dims_manual()
    else:
        screen_dims_auto()

    print(screen_dims)
    # todo: log screen dims
