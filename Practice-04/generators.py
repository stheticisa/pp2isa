# 1. Generator that yields squares up to N
def generate_squares(n):
    for i in range(n + 1):
        yield i ** 2

print("Squares up to N=10:")
for sq in generate_squares(10):
    print(sq, end=" ")
print("\n" + "=" * 50)

# 2. Generator to print even numbers between 0 and n
def even_numbers(n):
    for i in range(n + 1):
        if i % 2 == 0:
            yield i

n = int(input("Enter n for even numbers: "))
print("Even numbers between 0 and", n)
print(",".join(str(num) for num in even_numbers(n)))
print("=" * 50)

# 3. Generator for numbers divisible by 3 and 4 between 0 and n
def divisible_by_3_and_4(n):
    for i in range(n + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i

print("Numbers divisible by 3 and 4 up to 100:")
for num in divisible_by_3_and_4(100):
    print(num, end=" ")
print("\n" + "=" * 50)

# 4. Generator called squares to yield squares from a to b
def squares(a, b):
    for i in range(a, b + 1):
        yield i ** 2

print("Squares from 3 to 7:")
for val in squares(3, 7):
    print(val)
print("=" * 50)

# 5. Generator that returns all numbers from n down to 0
def countdown(n):
    while n >= 0:
        yield n
        n -= 1

print("Countdown from 10:")
for num in countdown(10):
    print(num, end=" ")
print()