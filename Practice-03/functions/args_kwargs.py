# Purpose: using *args and **kwargs

def describe_pet(*args, **kwargs):
    """Demonstrate flexible arguments."""
    print("Positional:", args)
    print("Keyword:", kwargs)

describe_pet("Dog", "Golden Retriever", age=5, vaccinated=True)
describe_pet()