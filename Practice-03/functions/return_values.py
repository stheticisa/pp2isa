# Purpose: return multiple values

def min_max_avg(numbers):
    """Return min, max, and average of a list."""
    return min(numbers), max(numbers), sum(numbers)/len(numbers)

low, high, avg = min_max_avg([10, 20, 30, 40])
print(low, high, avg)

print(min_max_avg([100]))  # single-element list