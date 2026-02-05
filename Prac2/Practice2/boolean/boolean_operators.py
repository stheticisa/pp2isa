# Purpose: evaluate conditions using boolean operators only

a = 10
b = 5
c = 10

# Basic comparisons
cond1 = a > b
cond2 = a == c
cond3 = b > a

# Logical operators
result_and = cond1 and cond2
result_or = cond1 or cond3
result_not = not cond2

# Mixed logical expressions
complex_1 = (a > b) and (b < c)
complex_2 = (a == b) or (a == c)
complex_3 = not (a < b)

# Operator precedence
precedence_1 = a > b and b > c
precedence_2 = a > b or b > c and a == c

# Boolean equality vs inequality
bool_compare_1 = cond1 == cond2
bool_compare_2 = cond1 != cond3

# Final outputs
print(result_and)
print(result_or)
print(result_not)

print(complex_1)
print(complex_2)
print(complex_3)

print(precedence_1)
print(precedence_2)

print(bool_compare_1)
print(bool_compare_2)
