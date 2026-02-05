# Loop through numbers 1 to 7
for i in range(1, 8):
    # Skip the number 4
    if i == 4:
        print("Skipping", i)
        continue
    print(i)

print("Loop finished")