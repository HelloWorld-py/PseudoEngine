# Author: Jacob Tsekrekos
# Date: Jun 19, 2018
# File: setup.py
# Description: sets up the window dimensions to be used by the window class if REGEDIT is restricted or WMIC doesn't exist
from ..DeviceInput import mouse_handler, mouse, ButtonCode
from ..engine_math import infinity
import os

screen_dims = [infinity, infinity]


def screen_dims_auto():
    global screen_dims
    ex = False
    start = False

    def end():
        nonlocal ex, start
        if mouse[ButtonCode.RIGHT]:
            ex = True

        if mouse[ButtonCode.LEFT]:
            start = True

    mouse_handler(end).start()

    minPos = [infinity, infinity]
    maxPos = [0, 0]

    while not start:
        pass

    while True:
        print("", minPos, "\n", maxPos)
        os.system("cls")

        a = mouse["pos"]
        if not a:
            continue

        # Set min Pos
        if a[0] < minPos[0]:
            minPos[0] = a[0]

        if a[1] < minPos[1]:
            minPos[1] = a[1]

        # setMaxPos
        if a[0] > maxPos[0]:
            maxPos[0] = a[0]

        if a[1] > maxPos[1]:
            maxPos[1] = a[1]

        if ex == True:
            break

    screen_dims = [sum(i) for i in zip(maxPos, minPos)]


def screen_dims_manual():
    global screen_dims
    while True:
        a = input("Screen Dimensions (l x h): ")
        try:
            screen_dims = map(int, a.split(" x "))
        except:
            print("Invalid input: Not a Number. Try again")
            continue


print("Please change your default font to be Consolas 16 (or another 8 x 16 font)")
input("Ready? ")

choice = 0
while True:
    print("(1)Type screen dimensions or (2)find them with the mouse? (1 or 2) ")
    try:
        choice = int(input(""))
        if not choice not in [1, 2]:
            raise TypeError()
        break
    except:
        print("Invalid input. Try again")

if choice == 1:
    screen_dims_manual()
else:
    screen_dims_auto()

print(screen_dims)
