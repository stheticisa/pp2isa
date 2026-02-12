# Purpose: positional, default, and keyword arguments

def power(base, exponent=2):
    """Raise base to a given exponent."""
    return base ** exponent

print(power(3))          # default exponent
print(power(3, 3))       # positional
print(power(base=2, exponent=5))  # keyword
print(power(4, exponent=3))       # mixed