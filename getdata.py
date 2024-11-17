from pymavlink import mavutil
import logging
import json
import os

# Set up logging
logging.basicConfig(filename='flight_data.log', level=logging.INFO, format='%(asctime)s %(message)s')

# Set up the UART connection
uart_port = 'COM7'  # Change this to your UART port
baud_rate = 460800  # Default baud rate for telemetry; adjust if needed

# Set up JSON logging
json_log_file = 'flight_data.json'
if not os.path.exists(json_log_file):
    with open(json_log_file, 'w') as file:
        json.dump([], file)

try:
    # Establish connection
    connection = mavutil.mavlink_connection(uart_port, baud=baud_rate)
    print(f"Connected to {uart_port} at {baud_rate} baud.")
    logging.info(f"Connected to {uart_port} at {baud_rate} baud.")

    # Wait for the heartbeat
    print("Waiting for heartbeat from the flight controller...")
    logging.info("Waiting for heartbeat from the flight controller...")
    connection.wait_heartbeat()
    print("Heartbeat received!")
    logging.info("Heartbeat received!")

    # Request data streams
    connection.mav.request_data_stream_send(
        connection.target_system, connection.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1  # Request all data streams at 10 Hz
    )

    # Fetch data in a loop
    while True:
        data_entry = {}

        # Fetch and log GPS data
        gps_msg = connection.recv_match(type='GPS_RAW_INT', blocking=True)
        if gps_msg:
            latitude = gps_msg.lat / 1e7  # Convert to decimal degrees
            longitude = gps_msg.lon / 1e7
            gps_altitude = gps_msg.alt / 1000  # Convert to meters
            gps_data = {
                "GPS": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "altitude_m": gps_altitude
                }
            }
            data_entry.update(gps_data)
            print(gps_data)
            logging.info(gps_data)

        # Fetch and log Rangefinder data
        rangefinder_msg = connection.recv_match(type='RANGEFINDER', blocking=True)
        if rangefinder_msg:
            rangefinder_distance = rangefinder_msg.distance  # In meters
            rangefinder_data = {
                "Rangefinder": {
                    "distance_m": rangefinder_distance
                }
            }
            data_entry.update(rangefinder_data)
            print(rangefinder_data)
            logging.info(rangefinder_data)

        # Fetch and log Altitude data
        altitude_msg = connection.recv_match(type='VFR_HUD', blocking=True)
        if altitude_msg:
            altitude = altitude_msg.alt  # In meters
            altitude_data = {
                "Altitude": {
                    "altitude_m": altitude
                }
            }
            data_entry.update(altitude_data)
            print(altitude_data)
            logging.info(altitude_data)

        # Fetch and log Attitude data
        attitude_msg = connection.recv_match(type='ATTITUDE', blocking=True)
        if attitude_msg:
            roll = attitude_msg.roll
            pitch = attitude_msg.pitch
            yaw = attitude_msg.yaw
            attitude_data = {
                "Attitude": {
                    "roll": roll,
                    "pitch": pitch,
                    "yaw": yaw
                }
            }
            data_entry.update(attitude_data)
            print(attitude_data)
            logging.info(attitude_data)

        # Fetch and log Battery Status data
        battery_msg = connection.recv_match(type='BATTERY_STATUS', blocking=True)
        if battery_msg:
            voltage = battery_msg.voltages[0] / 1000.0  # Convert to volts
            current = battery_msg.current_battery / 100.0  # Convert to amps
            battery_data = {
                "Battery": {
                    "voltage_v": voltage,
                    "current_a": current
                }
            }
            data_entry.update(battery_data)
            print(battery_data)
            logging.info(battery_data)

        # Write data entry to JSON file
        if data_entry:
            with open(json_log_file, 'r+') as file:
                data = json.load(file)
                data.append(data_entry)
                file.seek(0)
                json.dump(data, file, indent=4)

except KeyboardInterrupt:
    print("Exiting program.")
    logging.info("Exiting program.")
except Exception as e:
    error_message = f"Error: {e}"
    print(error_message)
    logging.error(error_message)
