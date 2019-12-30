import math

class Vec2:

    def __init__(self, x=0.0, y=0.0):
        self._x = x
        self._y = y

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def get_yx(self):
        return Vec2(self._y, self._x)

    def as_tuple(self):
        return self._x, self._y

    def __iter__(self):
        return iter(self.as_tuple())

    def __add__(self, other):
        if type(other) == Vec2:
            return Vec2(self._x + other.get_x(), self._y + other.get_y())
        else:
            return Vec2(self._x + other, self._y + other)

    def __sub__(self, other):
        if type(other) == Vec2:
            return Vec2(self._x - other.get_x(), self._y - other.get_y())
        else:
            return Vec2(self._x - other, self._y - other)

    def __mul__(self, other):
        if type(other) == Vec2:
            return Vec2(self._x * other.get_x(), self._y * other.get_y())
        else:
            return Vec2(self._x * other, self._y * other)

    def __truediv__(self, other):
        if type(other) == Vec2:
            return Vec2(self._x / other.get_x(), self._y / other.get_y())
        else:
            return Vec2(self._x / other, self._y / other)

    def __matmul__(self, other):
        return self._x * other.get_x() + self._y * other.get_y()

    def rotate(self, angle):
        cosine = math.cos(angle)
        sine = math.sin(angle)
        return Vec2(cosine * self._x - sine * self._y, sine * self._x + cosine * self._y)

    def dot(self, other):
        return self @ other

    def length(self):
        return math.sqrt(self._x ** 2 + self._y ** 2)

    def normalize(self):
        length = self.length()
        return Vec2(self._x / length, self._y / length)

    def lerp(self, other, factor):  # linear interpolation
        return Vec2(self._x * (1 - factor) + other.get_x() * factor, self._y * (1 - factor) + other.get_y() * factor)

    def __str__(self):
        return f'Vec2({self._x}, {self._y})'

    def __eq__(self, other):
        if type(other) != Vec2:
            return False
        return self._x == other.get_x() and self._y == other.get_y()
