# Write (overwrite)
f = open("example.txt", "w")
f.write("Hello, this is new content.")
f.close()

# Append
f = open("example.txt", "a")
f.write("\nThis line is appended.")
f.close()