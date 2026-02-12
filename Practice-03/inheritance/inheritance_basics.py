# Purpose: parent and child class relationships

class Animal:
    def speak(self):
        return "Generic sound"

class Dog(Animal):
    def speak(self):
        return "Woof!"

animal = Animal()
dog = Dog()

print(animal.speak())
print(dog.speak())