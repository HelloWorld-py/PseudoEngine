"""Gamepad inputs

Inputs aims to provide easy to use, cross-platform, user input device
support for Python. I.e. keyboards, mice, gamepads, etc.

Currently supported platforms are the Raspberry Pi, Linux, Windows and
Mac OS X.

"""

# Copyright (c) 2016, Zeth
# All rights reserved.
#
# BSD Licence
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#     * Neither the name of the copyright holder nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from __future__ import print_function
from __future__ import division

import os
import sys
import io
import glob
import struct
import platform
import math
import time
from warnings import warn
from itertools import count
from operator import itemgetter
from multiprocessing import Process, Pipe
import ctypes

__version__ = "0.1"

WIN = True if platform.system() == 'Windows' else False
MAC = True if platform.system() == 'Darwin' else False
NIX = True if platform.system() == 'Linux' else False

if WIN:
    # pylint: disable=wrong-import-position
    import ctypes.wintypes

    DWORD = ctypes.wintypes.DWORD
    HANDLE = ctypes.wintypes.HANDLE
    WPARAM = ctypes.wintypes.WPARAM
    LPARAM = ctypes.wintypes.WPARAM
    MSG = ctypes.wintypes.MSG
else:
    DWORD = ctypes.c_ulong
    HANDLE = ctypes.c_void_p
    WPARAM = ctypes.c_ulonglong
    LPARAM = ctypes.c_ulonglong
    MSG = ctypes.Structure

OLD = sys.version_info < (3, 4)


def chunks(raw):
    """Yield successive 24-sized chunks from raw."""
    for i in range(0, len(raw), 24):
        yield struct.unpack(EVENT_FORMAT, raw[i:i + 24])


def iter_unpack(raw):
    """Yield successive 24-sized chunks from message."""
    if OLD:
        return chunks(raw)
    else:
        return struct.iter_unpack(EVENT_FORMAT, raw)


# long, long, unsigned short, unsigned short, int
EVENT_FORMAT = str('llHHi')
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)

XINPUT_MAPPING = (
    (1, 0x11),
    (2, 0x11),
    (3, 0x10),
    (4, 0x10),
    (5, 0x13a),
    (6, 0x13b),
    (7, 0x13d),
    (8, 0x13e),
    (9, 0x136),
    (10, 0x137),
    (13, 0x130),
    (14, 0x131),
    (15, 0x134),
    (16, 0x133),
    (17, 0x11),
    ('l_thumb_x', 0x00),
    ('l_thumb_y', 0x01),
    ('left_trigger', 0x02),
    ('r_thumb_x', 0x03),
    ('r_thumb_y', 0x04),
    ('right_trigger', 0x05),
)

XINPUT_DLL_NAMES = (
    "XInput1_4.dll",
    "XInput9_1_0.dll",
    "XInput1_3.dll",
    "XInput1_2.dll",
    "XInput1_1.dll"
)

XINPUT_ERROR_DEVICE_NOT_CONNECTED = 1167
XINPUT_ERROR_SUCCESS = 0

DEVICE_PROPERTIES = (
    (0x00, "INPUT_PROP_POINTER"),  # needs a pointer
    (0x01, "INPUT_PROP_DIRECT"),  # direct input devices
    (0x02, "INPUT_PROP_BUTTONPAD"),  # has button(s) under pad
    (0x03, "INPUT_PROP_SEMI_MT"),  # touch rectangle only
    (0x04, "INPUT_PROP_TOPBUTTONPAD"),  # softbuttons at top of pad
    (0x05, "INPUT_PROP_POINTING_STICK"),  # is a pointing stick
    (0x06, "INPUT_PROP_ACCELEROMETER"),  # has accelerometer
    (0x1f, "INPUT_PROP_MAX"),
    (0x1f + 1, "INPUT_PROP_CNT"))

EVENT_TYPES = (
    (0x00, "Sync"),
    (0x01, "Key"),
    (0x02, "Relative"),
    (0x03, "Absolute"),
    (0x04, "Misc"),
    (0x05, "Switch"),
    (0x11, "LED"),
    (0x12, "Sound"),
    (0x14, "Repeat"),
    (0x15, "ForceFeedback"),
    (0x16, "Power"),
    (0x17, "ForceFeedbackStatus"),
    (0x1f, "Max"),
    (0x1f + 1, "Current"))

SYNCHRONIZATION_EVENTS = (
    (0, "SYN_REPORT"),
    (1, "SYN_CONFIG"),
    (2, "SYN_MT_REPORT"),
    (3, "SYN_DROPPED"),
    (0xf, "SYN_MAX"),
    (0xf + 1, "SYN_CNT"))

KEYS_AND_BUTTONS = (
    (0x130, "BTN_GAMEPAD"),
    (0x130, "BTN_SOUTH"),
    (0x131, "BTN_EAST"),
    (0x132, "BTN_C"),
    (0x133, "BTN_NORTH"),
    (0x134, "BTN_WEST"),
    (0x135, "BTN_Z"),
    (0x136, "BTN_TL"),
    (0x137, "BTN_TR"),
    (0x138, "BTN_TL2"),
    (0x139, "BTN_TR2"),
    (0x13a, "BTN_SELECT"),
    (0x13b, "BTN_START"),
    (0x13c, "BTN_MODE"),
    (0x13d, "BTN_THUMBL"),
    (0x13e, "BTN_THUMBR"),
    (0x220, "BTN_DPAD_UP"),
    (0x221, "BTN_DPAD_DOWN"),
    (0x222, "BTN_DPAD_LEFT"),
    (0x223, "BTN_DPAD_RIGHT"),
    (0x2ff, "KEY_MAX"),
    (0x2ff + 1, "KEY_CNT"))

ABSOLUTE_AXES = (
    (0x00, "ABS_LX"),
    (0x01, "ABS_LY"),
    (0x02, "ABS_LZ"),
    (0x03, "ABS_RX"),
    (0x04, "ABS_RY"),
    (0x05, "ABS_RZ"),
    (0x10, "ABS_DPAD0X"),
    (0x11, "ABS_DPAD0Y"),
    (0x12, "ABS_DPAD1X"),
    (0x13, "ABS_DPAD1Y"),
    (0x14, "ABS_DPAD2X"),
    (0x15, "ABS_DPAD2Y"),
    (0x16, "ABS_DPAD3X"),
    (0x17, "ABS_DPAD3Y"),
    (0x3f, "ABS_MAX"),
    (0x3f + 1, "ABS_CNT"))

SWITCH_EVENTS = (
    (0x00, "SW_LID"),  # set = lid shut
    (0x01, "SW_TABLET_MODE"),  # set = tablet mode
    (0x02, "SW_HEADPHONE_INSERT"),  # set = inserted
    (0x03, "SW_RFKILL_ALL"),  # rfkill master switch, type "any"
    (0x04, "SW_MICROPHONE_INSERT"),  # set = inserted
    (0x05, "SW_DOCK"),  # set = plugged into dock
    (0x06, "SW_LINEOUT_INSERT"),  # set = inserted
    (0x07, "SW_JACK_PHYSICAL_INSERT"),  # set = mechanical switch set
    (0x08, "SW_VIDEOOUT_INSERT"),  # set = inserted
    (0x09, "SW_CAMERA_LENS_COVER"),  # set = lens covered
    (0x0a, "SW_KEYPAD_SLIDE"),  # set = keypad slide out
    (0x0b, "SW_FRONT_PROXIMITY"),  # set = front proximity sensor active
    (0x0c, "SW_ROTATE_LOCK"),  # set = rotate locked/disabled
    (0x0d, "SW_LINEIN_INSERT"),  # set = inserted
    (0x0e, "SW_MUTE_DEVICE"),  # set = device disabled
    (0x0f, "SW_MAX"),
    (0x0f + 1, "SW_CNT"))

MISC_EVENTS = (
    (0x00, "MSC_SERIAL"),
    (0x01, "MSC_PULSELED"),
    (0x02, "MSC_GESTURE"),
    (0x03, "MSC_RAW"),
    (0x04, "MSC_SCAN"),
    (0x05, "MSC_TIMESTAMP"),
    (0x07, "MSC_MAX"),
    (0x07 + 1, "MSC_CNT"))

LEDS = (
    (0x00, "LED_NUML"),
    (0x01, "LED_CAPSL"),
    (0x02, "LED_SCROLLL"),
    (0x03, "LED_COMPOSE"),
    (0x04, "LED_KANA"),
    (0x05, "LED_SLEEP"),
    (0x06, "LED_SUSPEND"),
    (0x07, "LED_MUTE"),
    (0x08, "LED_MISC"),
    (0x09, "LED_MAIL"),
    (0x0a, "LED_CHARGING"),
    (0x0f, "LED_MAX"),
    (0x0f + 1, "LED_CNT"))

AUTOREPEAT_VALUES = (
    (0x00, "REP_DELAY"),
    (0x01, "REP_PERIOD"),
    (0x01, "REP_MAX"),
    (0x01 + 1, "REP_CNT"))

SOUNDS = (
    (0x00, "SND_CLICK"),
    (0x01, "SND_BELL"),
    (0x02, "SND_TONE"),
    (0x07, "SND_MAX"),
    (0x07 + 1, "SND_CNT"))

# THING SING That thing can sing!
# SONG LONG A long, long song.
# Good-bye, Thing. You sing too long.
# pylint: disable=too-many-lines

# We have yet to support force feedback but probably should
# eventually:

FORCE_FEEDBACK = ()  # Motor in gamepad
FORCE_FEEDBACK_STATUS = ()  # Status of motor

POWER = ()  # Power switch

# These two are internal workings of evdev we probably will never care
# about.

MAX = ()
CURRENT = ()

EVENT_MAP = (
    ('types', EVENT_TYPES),
    ('type_codes', ((GP_value, GP_key) for GP_key, GP_value in EVENT_TYPES)),
    ('xpad', XINPUT_MAPPING),
    ('Sync', SYNCHRONIZATION_EVENTS),
    ('Key', KEYS_AND_BUTTONS),
    ('Absolute', ABSOLUTE_AXES),
    ('Misc', MISC_EVENTS),
    ('Switch', SWITCH_EVENTS),
    ('LED', LEDS),
    ('Sound', SOUNDS),
    ('Repeat', AUTOREPEAT_VALUES),
    ('ForceFeedback', FORCE_FEEDBACK),
    ('Power', POWER),
    ('ForceFeedbackStatus', FORCE_FEEDBACK_STATUS),
    ('Max', MAX),
    ('Current', CURRENT))


# Now comes all the structs we need to parse the infomation coming
# from Windows.
class XinputGamepad(ctypes.Structure):
    """Describes the current state of the Xbox 360 Controller.

    For full details see Microsoft's documentation:

    https://msdn.microsoft.com/en-us/library/windows/desktop/
    microsoft.directx_sdk.reference.xinput_gamepad%28v=vs.85%29.aspx

    """
    # pylint: disable=too-few-public-methods
    _fields_ = [
        ('buttons', ctypes.c_ushort),  # wButtons
        ('left_trigger', ctypes.c_ubyte),  # bLeftTrigger
        ('right_trigger', ctypes.c_ubyte),  # bLeftTrigger
        ('l_thumb_x', ctypes.c_short),  # sThumbLX
        ('l_thumb_y', ctypes.c_short),  # sThumbLY
        ('r_thumb_x', ctypes.c_short),  # sThumbRx
        ('r_thumb_y', ctypes.c_short),  # sThumbRy
    ]


class XinputState(ctypes.Structure):
    """Represents the state of a controller.

    For full details see Microsoft's documentation:

    https://msdn.microsoft.com/en-us/library/windows/desktop/
    microsoft.directx_sdk.reference.xinput_state%28v=vs.85%29.aspx

    """
    # pylint: disable=too-few-public-methods
    _fields_ = [
        ('packet_number', ctypes.c_ulong),  # dwPacketNumber
        ('gamepad', XinputGamepad),  # Gamepad
    ]


class XinputVibration(ctypes.Structure):
    """Specifies motor speed levels for the vibration function of a
    controller.

    For full details see Microsoft's documentation:

    https://msdn.microsoft.com/en-us/library/windows/desktop/
    microsoft.directx_sdk.reference.xinput_vibration%28v=vs.85%29.aspx

    """
    # pylint: disable=too-few-public-methods
    _fields_ = [("wLeftMotorSpeed", ctypes.c_ushort),
                ("wRightMotorSpeed", ctypes.c_ushort)]


class PermissionDenied(IOError):
    """/dev/input not allowed by user.
    Common Linux problem."""
    pass


class UnpluggedError(RuntimeError):
    """The device requested is not plugged in."""
    pass


class UnknownEventType(IndexError):
    """We don't know what this event is."""
    pass


class UnknownEventCode(IndexError):
    """We don't know what this event is."""
    pass


class InputEvent(object):
    """A user event."""

    # pylint: disable=too-few-public-methods
    def __init__(self,
                 device,
                 event_info):
        self.device = device
        self.timestamp = event_info["timestamp"]
        self.code = event_info["code"]
        self.state = event_info["state"]
        self.ev_type = event_info["ev_type"]


class BaseListener(object):
    """Loosely emulate Evdev keyboard behaviour on other platforms.
    Listen (hook in Windows terminology) for key events then buffer
    them in a pipe.
    """

    def __init__(self, pipe):
        self.pipe = pipe
        self.app = None
        self.type_codes = {
            "Sync": 0x00,
            "Key": 0x01,
            "Relative": 0x02,
            "Absolute": 0x03,
            "Misc": 0x04
        }
        if not getattr(self, "codes", None):
            self.codes = None
        self.install_handle_input()

    def install_handle_input(self):
        """Install the input handler."""
        pass

    def uninstall_handle_input(self):
        """Un-install the input handler."""
        pass

    def __del__(self):
        """Clean up when deleted."""
        self.uninstall_handle_input()

    @staticmethod
    def get_timeval():
        """Get the time and make it into C style timeval."""
        frac, whole = math.modf(time.time())
        microseconds = math.floor(frac * 1000000)
        seconds = math.floor(whole)
        return seconds, microseconds

    def create_event_object(self,
                            event_type,
                            code,
                            value,
                            timeval=None):
        """Create an evdev style structure."""
        if not timeval:
            timeval = self.get_timeval()
        try:
            event_code = self.type_codes[event_type]
        except KeyError:
            raise UnknownEventType(
                "We don't know what kind of event a %s is.",
                event_type)
        event = struct.pack(EVENT_FORMAT,
                            timeval[0],
                            timeval[1],
                            event_code,
                            code,
                            value)
        return event

    def write_to_pipe(self, event_list):
        """Send event back to the mouse object."""
        self.pipe.send_bytes(b''.join(event_list))

    def emulate_wheel(self, data, direction, timeval):
        """Emulate rel values for the mouse wheel.

        In evdev, a single click forwards of the mouse wheel is 1 and
        a click back is -1. Windows uses 120 and -120. We floor divide
        the Windows number by 120. This is fine for the digital scroll
        wheels found on the vast majority of mice. It also works on
        the analogue ball on the top of the Apple mouse.

        What do the analogue scroll wheels found on 200 quid high end
        gaming mice do? If the lowest unit is 120 then we are okay. If
        they report changes of less than 120 units Windows, then this
        might be an unacceptable loss of precision. Needless to say, I
        don't have such a mouse to test one way or the other.

        """
        if direction == 'x':
            code = 0x06
        elif direction == 'z':
            # Not enitely sure if this exists
            code = 0x07
        else:
            code = 0x08

        if WIN:
            data = data // 120

        return self.create_event_object(
            "Relative",
            code,
            data,
            timeval)

    def emulate_rel(self, key_code, value, timeval):
        """Emulate the relative changes of the mouse cursor."""
        return self.create_event_object(
            "Relative",
            key_code,
            value,
            timeval)

    def emulate_press(self, key_code, scan_code, value, timeval):
        """Emulate a button press.

        Currently supports 5 buttons.

        The Microsoft documentation does not define what happens with
        a mouse with more than five buttons, and I don't have such a
        mouse.

        From reading the Linux sources, I guess evdev can support up
        to 255 buttons.

        Therefore, I guess we could support more buttons quite easily,
        if we had any useful hardware.
        """
        scan_event = self.create_event_object(
            "Misc",
            0x04,
            scan_code,
            timeval)
        key_event = self.create_event_object(
            "Key",
            key_code,
            value,
            timeval)
        return scan_event, key_event

    def sync_marker(self, timeval):
        """Separate groups of events."""
        return self.create_event_object(
            "Sync",
            0,
            0,
            timeval)

    def emulate_abs(self, x_val, y_val, timeval):
        """Emulate the absolute co-ordinates of the mouse cursor."""
        x_event = self.create_event_object(
            "Absolute",
            0x00,
            x_val,
            timeval)
        y_event = self.create_event_object(
            "Absolute",
            0x01,
            y_val,
            timeval)
        return x_event, y_event


class InputDevice(object):
    """A user input device."""

    # pylint: disable=too-many-instance-attributes
    def __init__(self, manager, device_path,
                 char_path_override=None,
                 read_size=1):
        self.read_size = read_size
        self.manager = manager
        self._device_path = device_path
        self.protocol, _, self.device_type = self._get_path_infomation()

        if char_path_override:
            self._character_device_path = char_path_override
        else:
            self._character_device_path = os.path.realpath(device_path)
        self._character_file = None

        if WIN or MAC:
            self.__pipe = None
            self._listener = None
        else:
            with open("/sys/class/input/%s/device/name" %
                              self.get_char_name()) as name_file:
                self.name = name_file.read().strip()

    def _get_path_infomation(self):
        """Get useful infomation from the device path."""
        long_identifier = self._device_path.split('/')[4]
        protocol, remainder = long_identifier.split('-', 1)
        identifier, _, device_type = remainder.rsplit('-', 2)
        return (protocol, identifier, device_type)

    def get_char_name(self):
        """Get short version of char device name."""
        return self._character_device_path.split('/')[-1]

    def __str__(self):
        return self.name

    def __repr__(self):
        return '%s.%s("%s")' % (
            self.__module__,
            self.__class__.__name__,
            self._device_path)

    @property
    def _character_device(self):
        if not self._character_file:
            if WIN:
                self._character_file = io.BytesIO()
                return self._character_file
            try:
                self._character_file = io.open(
                    self._character_device_path, 'rb')
            except IOError as err:
                if err.errno == 13:
                    raise PermissionDenied(
                        "The user (that this program is being run as) does "
                        "not have permission to access the input events, "
                        "check groups and permissions, for example, on "
                        "Debian, the user needs to be in the input group.")
                else:
                    raise
        return self._character_file

    def __iter__(self):
        while True:
            event = self._do_iter()
            if event:
                yield event

    def _get_data(self, read_size):
        """Get data from the character device."""
        return self._character_device.read(read_size)

    @staticmethod
    def _get_target_function():
        """Get the correct target function. This is only used by Windows
        subclasses."""
        return False

    def _do_iter(self):
        if self.read_size:
            read_size = EVENT_SIZE * self.read_size
        else:
            read_size = EVENT_SIZE
        data = self._get_data(read_size)
        if not data:
            return
        evdev_objects = iter_unpack(data)
        events = [self._make_event(*event) for event in evdev_objects]
        return events

    # pylint: disable=too-many-arguments
    def _make_event(self, tv_sec, tv_usec, ev_type, code, value):
        event_type = self.manager.get_event_type(ev_type)
        eventinfo = {
            "ev_type": event_type,
            "state": value,
            "timestamp": tv_sec + (tv_usec / 1000000),
            "code": self.manager.get_event_string(event_type, code)
        }

        return InputEvent(self, eventinfo)

    def read(self):
        """Read the next input event."""
        return next(iter(self))

    @property
    def _pipe(self):
        """On Windows we use a pipe to emulate a Linux style character
        buffer."""
        if NIX:
            return None

        if not self.__pipe:
            target_function = self._get_target_function()
            if not target_function:
                return None

            self.__pipe, child_conn = Pipe(duplex=False)
            self._listener = Process(target=target_function,
                                     args=(child_conn,))
            self._listener.start()
        return self.__pipe

    def __del__(self):
        if 'WIN' in globals() or 'MAC' in globals():
            if WIN or MAC:
                if self.__pipe:
                    self._listener.terminate()


class GamePad(InputDevice):
    """A gamepad or other joystick-like device."""

    def __init__(self, manager, device_path,
                 char_path_override=None):
        super(GamePad, self).__init__(manager,
                                      device_path,
                                      char_path_override)
        if WIN:
            if "Microsoft_Corporation_Controller" in self._device_path:
                self.name = "Microsoft X-Box 360 pad"
                identifier = self._get_path_infomation()[1]
                self.__device_number = int(identifier.split('_')[-1])
                self.__received_packets = 0
                self.__missed_packets = 0
                self.__last_state = self.__read_device()

    def __iter__(self):
        while True:
            if WIN:
                self.__check_state()
            event = self._do_iter()
            if event:
                yield event

    def __check_state(self):
        """On Windows, check the state and fill the event character device."""
        state = self.__read_device()
        if not state:
            raise UnpluggedError(
                "Gamepad %d is not connected" % self.__device_number)
        if state.packet_number != self.__last_state.packet_number:
            # state has changed, handle the change
            self.__handle_changed_state(state)
            self.__last_state = state

    @staticmethod
    def __get_timeval():
        """Get the time and make it into C style timeval."""
        frac, whole = math.modf(time.time())
        microseconds = math.floor(frac * 1000000)
        seconds = math.floor(whole)
        return seconds, microseconds

    def create_event_object(self,
                            event_type,
                            code,
                            value,
                            timeval=None):
        """Create an evdev style object."""
        if not timeval:
            timeval = self.__get_timeval()
        try:
            event_code = self.manager.codes['type_codes'][event_type]
        except KeyError:
            raise UnknownEventType(
                "We don't know what kind of event a %s is.",
                event_type)
        event = struct.pack(EVENT_FORMAT,
                            timeval[0],
                            timeval[1],
                            event_code,
                            code,
                            value)
        return event

    def __write_to_character_device(self, event_list, timeval=None):
        """Emulate the Linux character device on other platforms such as
        Windows."""
        # Remember the position of the stream
        pos = self._character_device.tell()
        # Go to the end of the stream
        self._character_device.seek(0, 2)
        # Write the new data to the end
        for event in event_list:
            self._character_device.write(event)
        # Add a sync marker
        sync = self.create_event_object("Sync", 0, 0, timeval)
        self._character_device.write(sync)
        # Put the stream back to its original position
        self._character_device.seek(pos)

    def __handle_changed_state(self, state):
        """
        we need to pack a struct with the following five numbers:
        tv_sec, tv_usec, ev_type, code, value

        then write it using __write_to_character_device

        seconds, mircroseconds, ev_type, code, value
        time we just use now
        ev_type we look up
        code we look up
        value is 0 or 1 for the buttons
        axis value is maybe the same as Linux? Hope so!
        """
        timeval = self.__get_timeval()
        events = self.__get_button_events(state, timeval)
        events.extend(self.__get_axis_events(state, timeval))
        if events:
            self.__write_to_character_device(events, timeval)

    def __map_button(self, button):
        """Get the linux xpad code from the Windows xinput code."""
        _, start_code, start_value = button
        value = start_value
        ev_type = "Key"
        code = self.manager.codes['xpad'][start_code]
        if 1 <= start_code <= 4:
            ev_type = "Absolute"
        if start_code == 1 and start_value == 1:
            value = -1
        elif start_code == 3 and start_value == 1:
            value = -1
        return code, value, ev_type

    def __map_axis(self, axis):
        """Get the linux xpad code from the Windows xinput code."""
        start_code, start_value = axis
        value = start_value
        code = self.manager.codes['xpad'][start_code]
        return code, value

    def __get_button_events(self, state, timeval=None):
        """Get the button events from xinput."""
        changed_buttons = self.__detect_button_events(state)
        events = self.__emulate_buttons(changed_buttons, timeval)
        return events

    def __get_axis_events(self, state, timeval=None):
        """Get the stick events from xinput."""
        axis_changes = self.__detect_axis_events(state)
        events = self.__emulate_axis(axis_changes, timeval)
        return events

    def __emulate_axis(self, axis_changes, timeval=None):
        """Make the axis events use the Linux style format."""
        events = []
        for axis in axis_changes:
            code, value = self.__map_axis(axis)
            event = self.create_event_object(
                "Absolute",
                code,
                value,
                timeval=timeval)
            events.append(event)
        return events

    def __emulate_buttons(self, changed_buttons, timeval=None):
        """Make the button events use the Linux style format."""
        events = []
        for button in changed_buttons:
            code, value, ev_type = self.__map_button(button)
            event = self.create_event_object(
                ev_type,
                code,
                value,
                timeval=timeval)
            events.append(event)
        return events

    @staticmethod
    def __gen_bit_values(number):
        """
        Return a zero or one for each bit of a numeric value up to the most
        significant 1 bit, beginning with the least significant bit.
        """
        number = int(number)
        while number:
            yield number & 0x1
            number >>= 1

    def __get_bit_values(self, number, size=32):
        """Get bit values as a list for a given number"""
        res = list(self.__gen_bit_values(number))
        res.reverse()
        # 0-pad the most significant bit
        res = [0] * (size - len(res)) + res
        return res

    def __detect_button_events(self, state):
        changed = state.gamepad.buttons ^ self.__last_state.gamepad.buttons
        changed = self.__get_bit_values(changed, 16)
        buttons_state = self.__get_bit_values(state.gamepad.buttons, 16)
        changed.reverse()
        buttons_state.reverse()
        button_numbers = count(1)
        changed_buttons = list(
            filter(itemgetter(0),
                   list(zip(changed, button_numbers, buttons_state))))
        # returns for example [(1,15,1)] type, code, value?
        return changed_buttons

    def __detect_axis_events(self, state):
        # axis fields are everything but the buttons
        # pylint: disable=protected-access
        # Attribute name _fields_ is special name set by ctypes
        axis_fields = dict(XinputGamepad._fields_)
        axis_fields.pop('buttons')
        changed_axes = []

        # Ax_type might be useful when we support high-level deadzone
        # methods.
        # pylint: disable=unused-variable
        for axis, ax_type in list(axis_fields.items()):
            old_val = getattr(self.__last_state.gamepad, axis)
            new_val = getattr(state.gamepad, axis)
            if old_val != new_val:
                changed_axes.append((axis, new_val))
        return changed_axes

    def __read_device(self):
        """Read the state of the gamepad."""
        state = XinputState()
        res = self.manager.xinput.XInputGetState(
            self.__device_number, ctypes.byref(state))
        if res == XINPUT_ERROR_SUCCESS:
            return state
        if res != XINPUT_ERROR_DEVICE_NOT_CONNECTED:
            raise RuntimeError(
                "Unknown error %d attempting to get state of device %d" % (
                    res, self.__device_number))
            # else return None (device is not connected)

    def set_vibration(self, left_motor, right_motor):
        """Control the speed of both motors seperately
        Set between 0 and 1"""
        if WIN:
            # Set up function argument types and return type
            xinput_set_state = self.manager.xinput.XInputSetState
            xinput_set_state.argtypes = [
                ctypes.c_uint, ctypes.POINTER(XinputVibration)]
            xinput_set_state.restype = ctypes.c_uint

            vibration = XinputVibration(
                int(left_motor * 65535), int(right_motor * 65535))
            xinput_set_state(self.__device_number, ctypes.byref(vibration))
        else:
            print("Not implemented yet. Coming soon.")


class OtherDevice(InputDevice):
    """A device of which its is type is either undetectable or has not
    been implemented yet.
    """
    pass


class RawInputDeviceList(ctypes.Structure):
    """
    Contains information about a raw input device.

    For full details see Microsoft's documentation:

    http://msdn.microsoft.com/en-us/library/windows/desktop/
    ms645568(v=vs.85).aspx
    """
    # pylint: disable=too-few-public-methods
    _fields_ = [
        ("hDevice", HANDLE),
        ("dwType", DWORD)
    ]


class DeviceManager(object):
    """Provides access to all connected and detectible user input
    devices."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        self.codes = {key: dict(value) for key, value in EVENT_MAP}
        self.gamepads = []
        self.all_devices = []
        self.xinput = None
        if WIN:
            self._raw_device_counts = {
                'otherhid': 0,
                'unknown': 0
            }
            self._find_devices_win()
        else:
            self._find_devices()
        self._update_all_devices()

    def _update_all_devices(self):
        """Update the all_devices list."""
        self.all_devices.extend(self.gamepads)

    def _parse_device_path(self, device_path, char_path_override=None):
        """Parse each device and add to the approriate list."""
        try:
            device_type = device_path.rsplit('-', 1)[1]
        except IndexError:
            warn("The following device path was skipped as it could "
                 "not be parsed: %s" % device_path, RuntimeWarning)
            return

        if device_type == 'joystick':
            self.gamepads.append(GamePad(self,
                                         device_path,
                                         char_path_override))

    def _find_xinput(self):
        """Find most recent xinput library."""
        for dll in XINPUT_DLL_NAMES:
            try:
                self.xinput = getattr(ctypes.windll, dll)
            except OSError:
                pass
            else:
                # We found an xinput driver
                break
        else:
            # We didn't find an xinput library
            warn("No xinput driver dll found, gamepads not supported.")

    def _find_devices_win(self):
        """Find devices on Windows."""
        self._find_xinput()
        self._detect_gamepads()
        self._count_devices()

    def _detect_gamepads(self):
        """Find gamepads."""
        state = XinputState()
        # Windows allows up to 4 gamepads.
        for device_number in range(4):
            res = self.xinput.XInputGetState(
                device_number, ctypes.byref(state))
            if res == XINPUT_ERROR_SUCCESS:
                # We found a gamepad
                device_path = (
                    "/dev/input/by_id/" +
                    "usb-Microsoft_Corporation_Controller_%s-event-joystick"
                    % device_number)
                self.gamepads.append(GamePad(self, device_path))
                continue
            if res != XINPUT_ERROR_DEVICE_NOT_CONNECTED:
                raise RuntimeError(
                    "Unknown error %d attempting to get state of device %d"
                    % (res, device_number))

    def _count_devices(self):
        """See what Windows' GetRawInputDeviceList wants to tell us.

        For now, we are just seeing if there is at least one keyboard
        and/or mouse attached.

        GetRawInputDeviceList could be used to help distinguish between
        different keyboards and mice on the system in the way Linux
        can. However, Roma uno die non est condita.

        """
        number_of_devices = ctypes.c_uint()

        if ctypes.windll.user32.GetRawInputDeviceList(
                ctypes.POINTER(ctypes.c_int)(),
                ctypes.byref(number_of_devices),
                ctypes.sizeof(RawInputDeviceList)) == -1:
            warn("Call to GetRawInputDeviceList was unsuccessful."
                 "We have no idea if a mouse or keyboard is attached.",
                 RuntimeWarning)
            return

        devices_found = (RawInputDeviceList * number_of_devices.value)()

        if ctypes.windll.user32.GetRawInputDeviceList(
                devices_found,
                ctypes.byref(number_of_devices),
                ctypes.sizeof(RawInputDeviceList)) == -1:
            warn("Call to GetRawInputDeviceList was unsuccessful."
                 "We have no idea if a mouse or keyboard is attached.",
                 RuntimeWarning)
            return

        for device in devices_found:
            if device.dwType == 2:
                self._raw_device_counts['otherhid'] += 1
            else:
                self._raw_device_counts['unknown'] += 1

    def _find_devices(self):
        """Find available devices."""
        length = self._find_by_id()
        if not length:
            self._find_by_path()
        self._find_special()

    def _find_by_path(self):
        """Find devices by path."""
        by_path = glob.glob('/dev/input/by-path/*-event-*')
        for device_path in by_path:
            self._parse_device_path(device_path)

    def _find_by_id(self):
        """Find devices by id."""
        # Start with everything given an id
        # I.e. those with fully correct kernel drivers
        by_id = glob.glob('/dev/input/by-id/*-event-*')
        for device_path in by_id:
            self._parse_device_path(device_path)
        return len(by_id)

    def _get_char_names(self):
        """Get a list of already found devices."""
        return [device.get_char_name() for
                device in self.all_devices]

    def _find_special(self):
        """Look for special devices."""
        charnames = self._get_char_names()
        for eventdir in glob.glob('/sys/class/input/event*'):
            char_name = os.path.split(eventdir)[1]
            if char_name in charnames:
                continue
            name_file = os.path.join(eventdir, 'device', 'name')
            with open(name_file) as name_file:
                device_name = name_file.read().strip()
                if device_name in self.codes['specials']:
                    self._parse_device_path(
                        self.codes['specials'][device_name],
                        os.path.join('/dev/input', char_name))

    def __iter__(self):
        return iter(self.all_devices)

    def __getitem__(self, index):
        try:
            return self.all_devices[index]
        except IndexError:
            raise IndexError("list index out of range")

    def get_event_type(self, raw_type):
        """Convert the code to a useful string name."""
        try:
            return self.codes['types'][raw_type]
        except KeyError:
            raise UnknownEventType("We don't know this event type")

    def get_event_string(self, evtype, code):
        """Get the string name of the event."""
        if WIN and evtype == 'Key':
            # If we can map the code to a common one then do it
            try:
                code = self.codes['wincodes'][code]
            except KeyError:
                pass
        try:
            return self.codes[evtype][code]
        except KeyError:
            raise UnknownEventCode("We don't know this event.")
