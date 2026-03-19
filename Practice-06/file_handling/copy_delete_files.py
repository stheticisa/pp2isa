import os

# Copy file
f1 = open("example.txt", "r")
content = f1.read()
f1.close()

f2 = open("copy.txt", "w")
f2.write(content)
f2.close()

# Delete file if exists
if os.path.exists("copy.txt"):
    os.remove("copy.txt")
else:
    print("The file does not exist")