# 2018/04/20

def superscript(num):
    encoding = {
        "0": "\u2070",
        "1": "\u00B9",
        "2": "\u00B2",
        "3": "\u00B3",
        "4": "\u2074",
        "5": "\u2075",
        "6": "\u2076",
        "7": "\u2077",
        "8": "\u2078",
        "9": "\u2079",
        "+": "\u207A",
        "-": "\u207B",
        "(": "\u207D",
        ")": "\u207E"
    }
    num = str(num)
    out = ""
    for i in num:
        try:
            out += encoding[i]
        except KeyError:
            out += i
    return out


def subscript(num):
    encoding = {
        "0": "\u2080",
        "1": "\u2081",
        "2": "\u2082",
        "3": "\u2083",
        "4": "\u2084",
        "5": "\u2085",
        "6": "\u2086",
        "7": "\u2087",
        "8": "\u2088",
        "9": "\u2089",
        "+": "\u208A",
        "-": "\u208B",
        "(": "\u208D",
        ")": "\u208E"
    }
    num = str(num)
    out = ""
    for i in num:
        try:
            out += encoding[i]
        except KeyError:
            out += i

    return out


def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a


class NotInitialized(Exception):
    def __init__(self, msg):
        super().__init__(msg)


def convert(o, t):
    error = None

    try:
        return t._convert_to(o)
    except AttributeError:
        error = NotImplementedError("'{}' does not define '_convert_to(other)'".format(t.__name__))
    except Exception as e:
        error = e

    if error:
        raise error


class Infinity:
    def __ge__(self, other):
        return True

    def __lt__(self, other):
        return False

    def __eq__(self, other):
        if isinstance(other, Infinity):
            return True
        else:
            return False

    def __le__(self, other):
        return self == other

    def __gt__(self, other):
        return self != other

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return "\u221E"

    def __repr__(self):
        return str(self)


class Number:
    """
    'Number' template class used to simplify classification of number-types in this module
    """

    @staticmethod
    def _convert_to(value, key=None):
        """
        :param value: value of some type that is to be converted to a Number
        :param key: function applied must return a value that can be converted to a float
        :returns a Number type defined in Number.types()
        :raises TypeError
        """
        if isinstance(value, Number):
            return value

        if key is None:
            key = float
        try:
            value = key(value)
            return float(value)
        except:
            e = True
        if e:
            raise TypeError("Cannot be cast to Number ('{}')".format(value.__class__.__name__))

    def __neg__(self):
        error_info = "{}.{}({})".format(self.__class__.__name__, "__neg__", "self")
        raise NotImplementedError(error_info)

    def __add__(self, other):
        error_info = "{}.{}({})".format(self.__class__.__name__, "__add__", "self, other")
        raise NotImplementedError(error_info)

    def __radd__(self, other):
        if isinstance(other, Number.types()):
            return self + other
        elif isinstance(other, str):
            return other + str(self)

    def __sub__(self, other):
        error_info = "{}.{}({})".format(self.__class__.__name__, "__sub__", "self, other")
        raise NotImplementedError(error_info)

    def __rsub__(self, other):
        return -self + other

    def __mul__(self, other):
        error_info = "{}.{}({})".format(self.__class__.__name__, "__mul__", "self, other")
        raise NotImplementedError(error_info)

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        error_info = "{}.{}({})".format(self.__class__.__name__, "__truediv__", "self, other")
        raise NotImplementedError(error_info)

    def __rtruediv__(self, other):
        return self._make_type(other) / self

    def __eq__(self, other):
        error_info = "{}.{}({})".format(self.__class__.__name__, "__eq__", "self, other")
        raise NotImplementedError(error_info)

    def __ne__(self, other):
        return not self == other

    def simplify(self):
        error_info = "{}.{}({})".format(self.__class__.__name__, "simplify", "self")
        raise NotImplementedError(error_info)

    @classmethod
    def _make_type(cls, o):
        raise NotImplementedError(cls)

    @staticmethod
    def types():
        return float, int, Number


class Fraction(Number):
    def __init__(self, numerator, denominator):
        """
        :param numerator: A number
        :param denominator: A number
        :raises TypeError
        """
        if not (isinstance(numerator, Number.types() or isinstance(denominator, Number.types()))):
            numerator = convert(numerator, Number)
            denominator = convert(denominator, Number)

        if isinstance(numerator, float) or isinstance(denominator, float):
            multiplier1 = len(str(numerator).split(".")[-1])
            multiplier2 = len(str(numerator).split(".")[-1])
            multiplier = max(multiplier1, multiplier2)
            numerator = int(numerator * 10 ** multiplier)
            denominator = int(denominator * 10 ** multiplier)

        if isinstance(denominator, Fraction):
            numerator, denominator = numerator * denominator.denom, denominator.numer
        elif isinstance(denominator, Radical):
            # todo: add in once the radical has multiplication implimented
            pass

        if isinstance(numerator, Fraction):
            denominator *= numerator.denom
            numerator = numerator.numer

        self.__numer = numerator
        self.__denom = denominator

        self.simplify()

    def __float__(self):
        if self.__denom == 0:
            raise ZeroDivisionError
        return self.__numer / self.__denom

    def __int__(self):
        return self.__numer // self.__denom

    def __str__(self):
        f_nom = superscript(self.__numer) if self.__numer >= 0 else "-" + superscript(-self.__numer)
        return "{}\u2044{}".format(f_nom, subscript(self.__denom))

    def __repr__(self):
        return str(self)
    def __neg__(self):
        return Fraction(-self.__numer, self.__denom)

    def __add__(self, other):
        if not isinstance(other, Fraction):
            other = Fraction(other, 1)
            return self + other
        else:
            new_nom = self.__numer * other.denom + other.numer * self.__denom
            new_denom = self.__denom * other.denom

            new = Fraction(new_nom, new_denom)
            if new.denom == 1:
                return int(new.numer)
            else:
                return new

    def __sub__(self, other):
        if not isinstance(other, Fraction):
            other = Fraction(other, 1)
            return self - other
        else:
            new_nom = self.__numer * other.denom - other.numer * self.__denom
            new_denom = self.__denom * other.denom

            new = Fraction(new_nom, new_denom)
            if new.denom == 1:
                return int(new.numer)
            else:
                return new

    def __mul__(self, other):
        if not isinstance(other, Fraction):
            other = Fraction(other, 1)

        new_nom = self.__numer * other.numer
        new_denom = self.__denom * other.denom

        new = Fraction(new_nom, new_denom)
        if new.denom == 1:
            return int(new.numer)
        else:
            return new

    def __truediv__(self, other):
        if not isinstance(other, Fraction):
            other = Fraction(other, 1)
            return self / other

        new_nom = self.__numer * other.denom
        new_denom = self.__denom * other.numer

        new = Fraction(new_nom, new_denom)
        if new.denom == 1:
            return int(new.numer)
        else:
            return new

    def __rpow__(self, other):
        return (other ** self.__numer) ** (1 / self.__denom)

    def __pow__(self, power, modulo=None):
        return Fraction(self.__numer ** power, self.__denom ** power)

    def __eq__(self, other):
        other = Fraction._make_type(other)
        # self.simplify()
        if self.__numer == other.numer and self.__denom == other.denom:
            return True
        else:
            return False

    def __lt__(self, other):
        other = Fraction._make_type(other)
        return self.__numer / self.__denom < other.__numer / other.__denom

    def __le__(self, other):
        other = Fraction._make_type(other)
        return self.__numer / self.__denom <= other.__numer / other.__denom

    def __gt__(self, other):
        other = Fraction._make_type(other)
        return self.__numer / self.__denom > other.__numer / other.__denom

    def __ge__(self, other):
        other = Fraction._make_type(other)
        return self.__numer / self.__denom >= other.__numer / other.__denom

    def simplify(self):
        divisor = gcd(self.__numer, self.__denom)
        if divisor > 1:
            self.__numer //= divisor
            self.__denom //= divisor

            # return Fraction(self.__numer, self.__denom)

    @classmethod
    def _make_type(cls, o):
        if not isinstance(o, Fraction):
            o = Fraction(o, 1)
        return o

    def __copy__(self):
        return Fraction(self.__numer, self.__denom)

    @property
    def numer(self):
        return int(self.__numer)

    @property
    def denom(self):
        return int(self.__denom)


# todo: change Radicals API
class Radical(Number):
    # todo: add coefficients to value, check for numtype
    # todo: change order to be only exponent
    def __init__(self, value, order=None, coefficient=None):
        if order is None:
            order = 2

        # todo: Move to evaluation
        elif order == 0:
            raise ZeroDivisionError

        if coefficient is None:
            coefficient = 1

        if not (isinstance(value, Number.types() or
            isinstance(order, Number.types())) or
                    isinstance(coefficient, Number.types())):
            value = convert(value, Number)
            order = convert(order, Number)
            coefficient = convert(coefficient, Number)

        self.__coefficient = coefficient
        self.__base = value
        self.__root_order = Fraction(order, 1)
        self.__exponent = Fraction(1, order)

    def __float__(self):
        return float(self.__coefficient) * float(self.__base ** self.__exponent)

    def __int__(self):
        return int(float(self.__coefficient) * float(self.__base ** self.__exponent))

    def __mul__(self, other):
        if not isinstance(other, Radical):
            other = Radical(Radical(other, self.__exponent), self.__root_order)

        if self.__root_order != other.__root_order and self.__base != other.__base:
            # returns an Absolute
            pass
        else:
            if self.__root_order == other.__root_order:
                base = self.__base * other.__base
                root_order = self.__root_order
            else:
                base = self.__base
                root_order = self.__root_order * other.__root_order

            return Radical(base, root_order)
        pass

    def __str__(self):
        if self.__root_order == 1:
            return str(self.__base)
        elif self.__root_order.denom == 0:
            return "1"

        if int(self) == float(self):
            return str(int(self) * self.__coefficient)

        f_order = superscript(self.__root_order.numer) if self.__root_order.numer != 2 else ""
        f_exponent = superscript(self.__root_order.denom) if self.__root_order.denom != 1 else ""
        f_coef = ""
        if self.__coefficient != 1:
            f_coef += str(self.__coefficient) + "\u00b7" if self.__coefficient != -1 else "-"
        return "{}{}√({}{})".format(f_coef, f_order, self.__base, f_exponent)

    def __repr__(self):
        return str(self)

    def _make_type(self, o):
        return Radical(o ** self.__root_order, self.__root_order)

    def simplify(self):
        if self.__exponent.numer == 0:
            return 1

        if self.__exponent.numer > self.__exponent.denom:
            # factor out, returns a radical with coefficient
            exp = self.__exponent.numer // self.__exponent.denom
            self.__coefficient *= self.__base * exp
            self.__exponent -= Fraction(exp, self.__exponent.denom)
            print(exp, self)
        return self


class Exact(Number):
    def __init__(self, *components):
        self.__components = components

    def __str__(self):
        out = str(self.__components[0])
        for i in self.__components[1:]:
            out += ("+" if i > 0 else "") + i
        return out

    def __repr__(self):
        return str(self)


class Vector:
    _x, _y, _z = 0, 0, 0
    __is_initialized = False

    def _virt_init(self, x, y, z):
        self._x = x
        self._y = y
        self._z = z
        self.__is_initialized = True

    # @classmethod
    # def convert_to(cls, values, key=None):
    #     """
    #     :param values: An iterable that can be converted to a vector of NumberTypes
    #     :param key: function applied must return an iterable of NumberTypes
    #     :returns a Vector
    #     :raises TypeError
    #     """
    #     if isinstance(values, Vector):
    #         return values
    #
    #     try:
    #         if key:
    #             values = key(values)
    #
    #         values_f = [Number.convert_to(i) for i in values]
    #
    #         while len(values_f) < 4:
    #             values_f.append(0)
    #
    #         if cls.__name__ == "Vector":
    #             return Vector._virt_init(*values_f[:4])
    #
    #         elif cls.__name__ == "Vec3":
    #             return Vec3(*values_f[:3])
    #
    #         elif cls.__name__ == Vec2:
    #             return Vec2(*values_f[:2])
    #
    #         else:
    #             raise Exception
    #
    #     except:
    #         e = True
    #     if e:
    #         raise TypeError("Cannot be cast to a Vector ({}, key={})".format(type(values), key))
    def __abs__(self):
        return self.mag

    def __add__(self, other):
        return self.add(other)

    def __sub__(self, other):
        return self.sub(other)

    def __mul__(self, other):
        if isinstance(other, Vector):
            error = "Cannot implicitly multiply two Vectors"
            raise ValueError(error)
        if not isinstance(other, Number.types()):
            error = "Scalar is not a NumberType!"
            raise ValueError(error)

        x = self._x * other
        y = self._y * other
        z = self._z * other
        if self.__class__.__name__ == "Vec2":
            return Vec2(x, y)
        else:
            return Vec3(x, y, z)

    def __rmul__(self, other):
        return self * other

    def add(self, other):
        """
        :type other: Vector
        :returns Vector
        """
        if not self.__is_initialized:
            raise NotInitialized("Vector Object")

        x = self._x + other._x
        y = self._y + other._y
        if self.__class__.__name__ == "Vec3" or other.__class__.__name__ == "Vec3":
            z = self._z + other._z
            return Vec3(x, y, z)
        else:
            return Vec2(x, y)

    def sub(self, other):
        """
        :type other: Vector
        :returns Vector
        """
        if not self.__is_initialized:
            raise NotInitialized("Vector Object")

        x = self._x - other._x
        y = self._y - other._y
        if self.__class__.__name__ == "Vec3" or other.__class__.__name__ == "Vec3":
            z = self._z - other._z
            return Vec3(x, y, z)
        else:
            return Vec2(x, y)

    def dot(self, other):
        """
        :type other: Vector
        :returns Vector
        """
        if not self.__is_initialized:
            raise NotInitialized("Vector Object")

        product = (self._x * other._x) + (self._y * other._y)
        if self.__class__.__name__ == "Vec3" or other.__class__.__name__ == "Vec3":
            product += (self._z * other._z)

        return product

    def cross(self, other):
        """
        :type other: Vector
        :returns Vector
        """
        error_info = "{}.{}({})".format(self.__class__.__name__, "cross", "self, other")
        raise NotImplementedError(error_info)

    @property
    def mag(self):
        if not self.__is_initialized:
            raise NotInitialized("Vector Object")

        return Radical(self._x ** 2 + self._y ** 2 + self._z ** 2)

    @classmethod
    def from_points(cls, a, b):
        try:
            iter(a)
            iter(b)
        except:
            raise TypeError("Points must be iterable")

        if len(a) != len(b):
            raise TypeError("Points must have the same dimensions")

        components = map((lambda p: p[0] - p[1]), zip(a, b))
        if len(a) == 3 and len(b) == 3:
            return Vec3(*components)
        elif len(a) == 2 and len(b) == 2:
            return Vec2(*components)
        else:
            raise TypeError("Points must have either 2 or 3 dimensions")


class Vec2(Vector):
    def __init__(self, x, y):
        super()._virt_init(x, y, 0)

    def __str__(self):
        return "({},{})".format(self._x, self._y)

    def __repr__(self):
        return str(self)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._x = x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._y = y


class Vec3(Vector):
    def __init__(self, x, y, z):
        super()._virt_init(x, y, z)

    def __str__(self):
        return "({}, {}, {})".format(self._x, self._y, self._z)

    def __repr__(self):
        return str(self)
    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._x = x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._y = y

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, z):
        self._z = z


infinity = Infinity()

if __name__ == "__main__":
    a = Vector.from_points((1, 2), (2, 3))
    b = Vec3(1, 3, 2)

    print(2 ** -1)
    print(Radical(2, Fraction(2, 3)).simplify())
