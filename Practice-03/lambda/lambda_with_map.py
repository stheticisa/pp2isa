# Purpose: lambda with map()

numbers = [1, 2, 3, 4]
doubled = list(map(lambda x: x * 2, numbers))
print(doubled)

print(list(map(lambda x: x * 2, [])))  # empty list