# Purpose: instance vs class method

class Counter:
    count = 0  # class variable

    def __init__(self):
        Counter.count += 1

    def show(self):
        return f"Instance created. Total count: {Counter.count}"

obj1 = Counter()
obj2 = Counter()
print(obj1.show())
print(obj2.show())

print(Counter.count)  # direct access