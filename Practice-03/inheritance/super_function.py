# Purpose: using super() to call parent methods

class Person:
    def __init__(self, name):
        self.name = name

    def introduce(self):
        return f"My name is {self.name}"

class Student(Person):
    def __init__(self, name, grade):
        super().__init__(name)
        self.grade = grade

    def introduce(self):
        return super().introduce() + f" and I am in grade {self.grade}"

student = Student("Isa", "A")
print(student.introduce())