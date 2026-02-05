# Purpose: compare two numbers using if else only

a = 7
b = 7

# Main comparison
if a > b:
    result = "a is greater than b"
else:
    result = "a is not greater than b"

print(result)

# Equality check using if else
if a == b:
    equal_status = True
else:
    equal_status = False

print(equal_status)

# Logical condition with if else
if a >= b and a != b:
    relation = "greater"
else:
    relation = "equal or smaller"

print(relation)
