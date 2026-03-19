from functools import reduce

# map example
numbers = [1, 2, 3, 4]
squared = list(map(lambda x: x * x, numbers))
print(squared)

# filter example
even = list(filter(lambda x: x % 2 == 0, numbers))
print(even)

# reduce example
total = reduce(lambda x, y: x + y, numbers)
print(total)