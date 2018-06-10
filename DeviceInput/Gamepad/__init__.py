from ._base import DeviceManager, UnpluggedError
devices = DeviceManager()  # pylint: disable=invalid-name


def get_gamepad(index=0):
    """Get a single action from a gamepad."""
    try:
        gamepad = devices.gamepads[index]
    except IndexError:
        raise UnpluggedError("No gamepad found.")
    return gamepad.read()
