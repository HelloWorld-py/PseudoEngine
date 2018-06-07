from PIL import Image as _PIL_Image
import numpy as _numpy


class Hex:
    """Stores the values as an int and converts to a string for display"""
    def __init__(self, num):
        if isinstance(num, int):
            self.__val = num

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "{:#04x}".format(self.__val)

    def __int__(self):
        return self.__val

    def __eq__(self, other):
        try:
            other = int(other)
            return other == int(self)
        except:
            return False

    @classmethod
    def from_str(cls, num, delimiter=" "):
        num = num.split(delimiter)

        if len(num) == 1:
            return Hex(int(num, 16))
        else:
            out = []
            for i in num:
                out.append(Hex(int(i, 16)))
            return out

    @classmethod
    def from_int(cls, num):
        return Hex(num)

    @classmethod
    def from_bytes(cls, num):
        if len(num) > 1:
            return [Hex(n) for n in num]
        else:
            return Hex(num[0])

    @classmethod
    def from_array(cls, nums):
        out = []
        for i, num in enumerate(nums):
            if isinstance(num, int):
                out.append(Hex(num))
            elif isinstance(num, str):
                result = Hex.from_str(num)
                if isinstance(result, list):
                    out.extend(result)
                else:
                    out.append(result)
            elif isinstance(num, bytes):
                out.append(Hex.from_bytes(num))
        return out


# ITF STANDS FOR "IMAGE TEXT FORMAT" ---> TESTING PURPOSES

# class Image:
#     elements = []
#
#     supported = ["itf", "png"]
#     def __init__(self, fileName):
#         ext = fileName.split(".")[-1]
#         if ext not in Image.supported:
#             raise TypeError("File format '{}' not supported".format(ext))
#         self.__file = open(fileName, "rb")
#         self.__read()
#
#     def __read(self):
#         EOF = int(self.__file.seek(0, 2))
#         __raw = []
#         self.__file.seek(0)
#         while self.__file.tell() < EOF:
#             chunk = self.__file.read(1000)
#             print(chunk)
#             chunk = Hex.from_bytes(chunk)
#             if isinstance(chunk, list):
#                 __raw.extend(chunk)
#             else:
#                 __raw.append(chunk)
#
#         if __raw[:8] != Hex.from_str("89 50 4e 47 0d 0a 1a 0a"):
#             print("FORMAT NOT SUPPORTED")
#             print(__raw[:8])
#             return -1
#
#         print(__raw)
#
#     def __del__(self):
#         self.__file.close()


class Image:
    def __init__(self, path):
        __img = _PIL_Image.open(path)
        # __img.show()
        print(__img.info)
        self.__height = __img.height
        self.__width = __img.width
        self.pixels = list(__img.getdata())

    def __del__(self):
        del self.pixels

    @property
    def height(self):
        return self.__height

    @property
    def width(self):
        return self.__width


i = Image("../../resources/BCobble.png")
print(i.pixels[0])
print(i.height, i.width)