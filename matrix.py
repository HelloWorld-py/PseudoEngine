# row-major
# todo polish

class Matrix:
    """
    Stored row - displayed row major
    starts at upper left hand corner
    """
    def __init__(self, x, y, fill=None):
        if fill is None:
            fill = " "
        # self.elements = [["{:>04}".format(i*x + j) for i in range(y)] for j in range(x)]
        self.elements = [[fill for i in range(y)] for j in range(x)]
        self.__rows = x
        self.__columns = y

    def __str__(self):
        e = [[str(j) for j in i] for i in zip(*self.elements)]
        return "\n".join(" ".join(i) for i in e)

    def __getitem__(self, item):
        return self.elements[item]

    def writeMatrix(self, other, x=0, y=0):
        """
        :param x: x offset
        :param y: y offset
        :type other: Matrix
        :returns: None
        """

        for i in range(other.rows):
            if 0 > i + x or i + x >= self.rows:
                continue
            for j in range(other.columns):
                if 0 > j + y or j + y >= self.columns:
                    continue
                self[i + x][j + y] = other[i][j]

    @property
    def rows(self):
        return self.__rows

    @property
    def columns(self):
        return self.__columns


# class PopMatrix(Matrix):
#     __invalid = []
#
#     @property
#     def indices(self):
#         return [[x, y] for x in range(self.rows - 1) for y in range(self.columns - 1) if [x, y] not in self.__invalid]
#
#     def remove(self, index):
#         self.__invalid.append(index)
#
#     def clear(self):
#         self.__invalid = []


if __name__ == "__main__":
    m = Matrix(10, 5, "+")
    print(m, "\n")
    o = Matrix(5, 5, "0")
    m.writeMatrix(o, 6, -1)
    print(m)