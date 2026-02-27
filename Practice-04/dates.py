from datetime import datetime, timedelta

# 1. Subtract five days from current date
current_date = datetime.now()
five_days_ago = current_date - timedelta(days=5)
print("Current date:", current_date)
print("Five days ago:", five_days_ago)
print("=" * 50)

# 2. Print yesterday, today, tomorrow
today = datetime.now()
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)
print("Yesterday:", yesterday.date())
print("Today:", today.date())
print("Tomorrow:", tomorrow.date())
print("=" * 50)

# 3. Drop microseconds from datetime
dt_with_microseconds = datetime.now()
dt_without_microseconds = dt_with_microseconds.replace(microsecond=0)
print("With microseconds:", dt_with_microseconds)
print("Without microseconds:", dt_without_microseconds)
print("=" * 50)

# 4. Calculate two date difference in seconds
date1 = datetime(2026, 2, 27, 12, 0, 0)  # Example date
date2 = datetime(2026, 2, 27, 12, 13, 0) # Another example date
difference = date2 - date1
print("Date1:", date1)
print("Date2:", date2)
print("Difference in seconds:", difference.total_seconds())