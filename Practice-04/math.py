import math

# 1. Convert degree to radian
degree = 15
radian = degree * (math.pi / 180)
print(f"Input degree: {degree}")
print(f"Output radian: {radian:.6f}")  # formatted to 6 decimals

print("=" * 50)

# 2. Area of a trapezoid
height = 5
base1 = 5
base2 = 6
area_trapezoid = ((base1 + base2) / 2) * height
print(f"Height: {height}")
print(f"Base, first value: {base1}")
print(f"Base, second value: {base2}")
print(f"Expected Output: {area_trapezoid}")

print("=" * 50)

# 3. Area of a regular polygon
n_sides = 4
side_length = 25
# Formula: (n * s^2) / (4 * tan(pi/n))
area_polygon = (n_sides * side_length ** 2) / (4 * math.tan(math.pi / n_sides))
print(f"Input number of sides: {n_sides}")
print(f"Input the length of a side: {side_length}")
print(f"The area of the polygon is: {area_polygon}")

print("=" * 50)

# 4. Area of a parallelogram
base = 5
height_para = 6
area_para = base * height_para
print(f"Length of base: {base}")
print(f"Height of parallelogram: {height_para}")
print(f"Expected Output: {area_para}")