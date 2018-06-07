# Author: Jacob Tsekrekos
# Date: Mar 31, 2018
# File: evf.py
# Version 1.1 -> added Writer class, function that gets applied to all keys in the reader,
#                convert values to appropriate types
# Version

"""Interpreter for the Enclosed Variable File(.evf) format.
This is a module to work with enclosed variable files (".evf"s).

.evf is a format used to store variables in a debugging friendly format without making assumptions in the
underlying code. The variable names are enclosed in hard braces [] and the data is stored without any
specific identifiers. A variable without data can be stored as just the variable name without data
attached. This format is not whitespace sensitive.
e.g.
[variable]data
[NoData]

Current Version
- Keys are all strings
- stores values as NoneType, str, int, float, or bool

Example Usage to get variable in the global scope:
    settings = evf.Reader("settings.evf", str.lower)
    validSettings = {"height": None, "width": None, "frame rate": "waitLength", "border": None}

    for entry in settings:
        if entry in validSettings.keys():
            name = validSettings[entry] if validSettings[entry] is not None else entry
            globals()[name] = settings[entry]
"""
# todo add documentation, Impliment Unittest
import re


class Reader:
    """
    This class is used to take an open .evf and store the contents in a dictionary.
    To access the variables by name, use the .__getitem__ method on the class with the
    variable's name, or iterate through the object to get all items in the dictionary.
    """
    __keys = None
    __info = None

    __current_pos = None

    RE_keys = re.compile("(?<=\[)[^\]]+(?=])", re.VERBOSE)
    RE_values = re.compile("(?<=])[^\[\]]+((?=\[)|(?= ))")

    def __init__(self, fileName, keyFunc= None):
        """
        Reads the file and stores the variables in memory
        :type fileName: str
        """
        if keyFunc is None:
            keyFunc = lambda __key: __key

        file = open(fileName, "r")
        self.__file = file
        info = {}

        f_c = file.read() + " "

        keys = re.finditer(self.RE_keys, f_c)
        values = [value for value in re.finditer(self.RE_values, f_c)]

        for key in keys:
            if not values:
                info[key.group()] = None

            while values:
                value = values[0]

                if key.end() + 1 < value.start():
                    info[keyFunc(key.group())] = None
                    break

                values.pop(0)
                if key.end() + 1 == value.start():
                    info[keyFunc(key.group())] = value.group().strip()
                    break

        for key in info:
            if re.search("^\d+$",info[key]):
                info[key] = int(info[key])

            elif re.search("^\d+\.\d+$",info[key]):
                info[key] = float(info[key])

            elif re.search(re.compile("True", re.I), info[key]):
                info[key] = True

            elif re.search(re.compile("False", re.I), info[key]):
                info[key] = False

        self.__info = info
        self.__keys = [key for key in info.keys()]

    def __del__(self):
        self.__file.close()

    def __iter__(self):
        self.__current_pos = 0
        return self

    def __next__(self):
        if self.__current_pos < len(self.__keys):
            curr = self.__keys[self.__current_pos]
            self.__current_pos += 1
            return curr

        self.__current_pos = None
        raise StopIteration

    def __getitem__(self, item):
        """
        :raises KeyError
        :returns variable stored with item's name
        """
        if item not in self.__keys:
            raise KeyError
        return self.__info[item]

    # def map(self, keysFunc= None, output=False, **names_vars):
    #     if keysFunc:
    #         info = {keysFunc(key): self.__info[key] for key in self.__info}
    #         print(info)
    #     else:
    #         info = {key: self.__info[key] for key in self.__info}
    #
    #     for key in names_vars:
    #         if key in info.keys():
    #             name = names_vars[key] if names_vars[key] is not None else key
    #             globals()[name] = info[key]
    #         elif output:
    #             print("[Warning] '{}' was not found".format(key))


    @property
    def keys(self):
        """
        :returns a non-mutable copy of self.__keys
        """
        return tuple(self.__keys)


class Writer:
    def __init__(self, fileName):
        """
        Reads the __file and stores the variables in memory
        :type fileName: str
        """

        self.__file = open(fileName, "w")

    def write_from_globals(self, **vars_names):
        """
        only works if the file contains this class
        """
        # todo find a way to import this and get the new global scope
        with self.__file as outFile:
            for entry in vars_names:
                name = vars_names[entry] if vars_names[entry] is not None else entry
                if entry not in globals():
                    print("[Warning] Variable '{}' is undefined".format(entry))
                else:
                    outFile.write("[{}]{}\n".format(name, globals()[entry]))

    def write(self, **vars_vals):
        with self.__file as outFile:
            for name in vars_vals:
                outFile.write("[{}]{}\n".format(name, vars_vals[name]))

    def __del__(self):
        self.__file.close()


if __name__ == "__main__":
    width = 200
    height = 100

    writer = Writer("test.evf")
    writer.write(width=width, height=height)

    reader = Reader("test.evf", str.lower)

    for entry in reader:
        print(entry, reader[entry])
        globals()[entry] = reader[entry]

    # print(height)
    # print(width)
    # print(width+height)
