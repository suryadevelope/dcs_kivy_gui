# import time
# import obd

# connection = obd.OBD(portstr="/dev/ttyACM0") # auto-connects to USB or RF port

# cmd = obd.commands.SPEED # select an OBD command (sensor)


# response = connection.query(cmd) # send the command, and parse the response
# while True:
#     print(response.value) # returns unit-bearing values thanks to Pint
#     print(response.value.to("mph")) # user-friendly unit conversions
#     # time.sleep(1)




import obd  # Import the OBD library
import json  # Import the JSON library for file operations

# File to save the OBD data
output_file = "obd_data.json"

# Connect to the OBD-II adapter
connection = obd.OBD(portstr="/dev/ttyACM0")  # Automatically connects to the first available adapter

# Check if the connection is successful
# if connection.is_connected():
#     print("Successfully connected to the vehicle's OBD-II system.")
# else:
#     print("Failed to connect. Please check your OBD-II adapter.")
#     exit()

# Fetch all supported commands
supported_commands = connection.supported_commands

# Initialize a dictionary to store all data
obd_data = {}

print("Fetching OBD-II data...")

# Query each supported command and collect results
for command in supported_commands:
    response = connection.query(command)  # Query the command
    obd_data[command.name] = str(response.value)
   
# Save the OBD data to a JSON file
with open(output_file, "w") as file:
    json.dump(obd_data, file, indent=4)

print(f"OBD data saved to '{output_file}'.")

# Close the connection
connection.close()
