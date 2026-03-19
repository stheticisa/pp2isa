# Read entire file
f = open("example.txt", "r")
print(f.read())
f.close()

# Read first 5 characters
f = open("example.txt", "r")
print(f.read(5))
f.close()

# Read line by line
f = open("example.txt", "r")
for line in f:
    print(line.strip())
f.close()