import json

# Load JSON data from file
with open("sample-data.json") as f:
    data = json.load(f)

# Extract the list of interfaces
interfaces = data["imdata"]

# Print header
print("Interface Status")
print("=" * 79)
print("{:<50} {:<20} {:<7} {:<7}".format("DN", "Description", "Speed", "MTU"))
print("-" * 50 + " " + "-" * 20 + " " + "-" * 7 + " " + "-" * 7)

# Loop through and print each interface
for item in interfaces:
    attributes = item["l1PhysIf"]["attributes"]
    dn = attributes["dn"]
    descr = attributes.get("descr", "")
    speed = attributes["speed"]
    mtu = attributes["mtu"]
    print("{:<50} {:<20} {:<7} {:<7}".format(dn, descr, speed, mtu))