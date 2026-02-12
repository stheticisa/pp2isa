# Purpose: lambda with sorted()

students = [("Isa", 90), ("Tomiris", 85), ("Adolf", 95)]
sorted_students = sorted(students, key=lambda s: s[1], reverse=True)
print(sorted_students)

print(sorted(students, key=lambda s: len(s[0])))  # sort by name length