# Purpose: evaluate number relationships using short hand if
a = 10
b = 15

# Basic short hand if
result1 = "a is greater" if a > b else "a is not greater"

# Short hand if with equality
result2 = "equal" if a == b else "not equal"

# Short hand if with logical operators
result3 = "valid" if a < b and b <= 20 else "invalid"

# Nested short hand if (allowed but tricky)
result4 = "greater" if a > b else "equal" if a == b else "smaller"

# Short hand if returning boolean
result5 = True if a != b else False

print(result1)
print(result2)
print(result3)
print(result4)
print(result5)