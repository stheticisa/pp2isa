# Count from 1 upwards
count = 1

while True:
    print("Count:", count)
    # Stop when count reaches 5
    if count == 5:
        print("Breaking the loop")
        break
    count += 1

print("Loop ended")