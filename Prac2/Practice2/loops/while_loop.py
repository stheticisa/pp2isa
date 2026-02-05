# Initialize counter
count = 1

# Loop while count is less or equal to 5
while count <= 5:
    # Print current count and whether it is odd or even
    if count % 2 == 0:
        print(f"{count} is even")
    else:
        print(f"{count} is odd")

    count += 1

print("Loop finished")