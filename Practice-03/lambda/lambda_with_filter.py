# Purpose: lambda with filter()

words = ["apple", "banana", "cherry", "date"]
filtered = list(filter(lambda w: len(w) > 5, words))
print(filtered)

print(list(filter(lambda w: len(w) > 10, words)))  # all fail