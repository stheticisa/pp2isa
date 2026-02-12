# Purpose: method overriding

class Shape:
    def area(self):
        return 0

class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side * self.side

shape = Shape()
square = Square(5)

print(shape.area())
print(square.area())