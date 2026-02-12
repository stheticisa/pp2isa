# Purpose: multiple inheritance

class Flyer:
    def action(self):
        return "Flying"

class Swimmer:
    def action(self):
        return "Swimming"

class Duck(Flyer, Swimmer):
    def action(self):
        return super().action() + " and Swimming"

duck = Duck()
print(duck.action())