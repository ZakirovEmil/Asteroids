import math

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)
    
    def __mul__(self, value):
        return Vector(self.x * value, self.y * value)

    def rotated(self, angle):
        x = math.sin(-math.radians(angle))
        y = -math.cos(math.radians(angle))
        return Vector(x, y)

    def normolize(self):
        len = math.sqrt(math.pow(self.x, 2) + math.pow(self.y, 2))
        return Vector(self.x / len, self.y / len)

    def invert(self):
        return Vector(self.x, self.y) * -1

    def __str__(self):
        return "Vector: ({},{})".format(self.x, self.y)