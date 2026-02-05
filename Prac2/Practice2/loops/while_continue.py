count = 0

while count < 7:
    count += 1
    if count == 4:
        print("Skipping", count)
        continue
    print("Count is", count)

print("Loop finished")
