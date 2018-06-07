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

    @property
    def rows(self):
        return self.__rows

    @property
    def columns(self):
        return self.__columns

if __name__ == "__main__":
    m = Matrix(10, 5)
    print(m)
    print(m[1][3])