import re

# 1. Match 'a' followed by zero or more 'b'
pattern1 = r"ab*"
text1 = "abbb a ab abb"
print("1:", re.findall(pattern1, text1))


# 2. Match 'a' followed by two to three 'b'
pattern2 = r"ab{2,3}"
text2 = "ab abb abbb abbbb"
print("2:", re.findall(pattern2, text2))


# 3. Find sequences of lowercase letters joined with underscore
pattern3 = r"[a-z]+_[a-z]+"
text3 = "hello_world test_case Example_Test"
print("3:", re.findall(pattern3, text3))


# 4. Find sequences of one uppercase letter followed by lowercase letters
pattern4 = r"[A-Z][a-z]+"
text4 = "Hello world Python Regex Test"
print("4:", re.findall(pattern4, text4))


# 5. Match 'a' followed by anything ending in 'b'
pattern5 = r"a.*b"
text5 = "a123b axxb acb axyz"
print("5:", re.findall(pattern5, text5))


# 6. Replace space, comma, or dot with colon
text6 = "Hello, world. Python is fun"
result6 = re.sub(r"[ ,\.]", ":", text6)
print("6:", result6)


# 7. Convert snake_case to camelCase
def snake_to_camel(text):
    return re.sub(r"_([a-z])", lambda m: m.group(1).upper(), text)

print("7:", snake_to_camel("hello_world_python"))


# 8. Split a string at uppercase letters
text8 = "HelloWorldPythonTest"
result8 = re.findall(r"[A-Z][^A-Z]*", text8)
print("8:", result8)


# 9. Insert spaces between words starting with capital letters
text9 = "HelloWorldPythonTest"
result9 = re.sub(r"([A-Z])", r" \1", text9).strip()
print("9:", result9)


# 10. Convert camelCase to snake_case
def camel_to_snake(text):
    return re.sub(r"([A-Z])", r"_\1", text).lower()

print("10:", camel_to_snake("helloWorldPythonTest"))