import unittest
from vector import Vector


class TestVector(unittest.TestCase):
    def setUp(self):
        self.vector = Vector(1, 0)

    def test_add(self):
        vector = self.vector + self.vector
        print(vector.x, vector.y)
        self.assertEqual((vector.x, vector.y), (2, 0))

    def test_sub(self):
        vector = self.vector - self.vector
        print(vector.x, vector.y)
        self.assertEqual((vector.x, vector.y), (0, 0))

    def test_mul(self):
        vector = self.vector * 2
        print(vector.x, vector.y)
        self.assertEqual((vector.x, vector.y), (2, 0))

    def test_rotate(self):
        vector = self.vector.rotated(0)
        print(vector.x, vector.y)
        self.assertEqual((vector.x, vector.y), (0, -1))

    def test_str(self):
        str_vector = str(self.vector)
        self.assertEqual(str_vector, "Vector: (1,0)")

    def test_normolize(self):
        vector = Vector(3, 5).normolize()
        print(vector.x, vector.y)
        self.assertEqual((round(vector.x, 1), round(vector.y, 1)), (0.5, 0.9))

    def test_invert(self):
        vector = Vector(1, 1).invert()
        print(vector.x, vector.y)
        self.assertEqual((vector.x, vector.y), (-1, -1))


if __name__ == '__main__':
    unittest.main()
