# Purpose: __init__ constructor

class Student:
    def __init__(self, name, grade):
        self.name = name
        self.grade = grade

student1 = Student("Isa", "A")
student2 = Student("Tomiris", "B")

print(student1.name, student1.grade)
print(student2.name, student2.grade)

student1.grade = "A+"  # modify attribute
print(student1.grade)