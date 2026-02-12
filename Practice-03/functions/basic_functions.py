# Purpose: function definition and calling

def greet(name):
    """Return a personalized greeting."""
    return f"Hello, {name}!"

# Direct calls
print(greet("Isa"))
print(greet("Tomiris"))

# Edge case: empty string
print(greet(""))