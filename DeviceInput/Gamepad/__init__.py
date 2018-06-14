from ._base import DeviceManager, UnpluggedError
devices = DeviceManager()  # pylint: disable=invalid-name


def get_gamepad(index=0):
    """Get a single action from a gamepad. DOES NOT CHECK ERRORS ENSURE TO check_gamepad BEFORE USING"""

    gamepad = devices.gamepads[index]
    return gamepad.read()


def check_gamepad():
    """:returns True if alive else false"""
    # e = None

    try:
        devices.gamepads[0]
    except IndexError:
        return False

    # if e:
    #     # raise UnpluggedError  # instead?
    #     return False
    return True
