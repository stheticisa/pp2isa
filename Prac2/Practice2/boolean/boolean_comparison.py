# Purpose: analyze the relationship between two numbers using comparisons only

a = 14
b = 9

# Direct comparisons
is_greater = a > b
is_equal = a == b
is_smaller = a < b

# Comparison using expressions
difference = abs(a - b)
difference_small = difference <= 5
difference_large = difference > 10

# Chained comparisons
within_range = 5 < difference < 15

# Logical comparison results
valid_relation = is_greater and not is_equal
exclusive_relation = is_greater != is_smaller

# Final outputs
print(is_greater)
print(is_equal)
print(is_smaller)

print(difference_small)
print(difference_large)
print(within_range)

print(valid_relation)
print(exclusive_relation)