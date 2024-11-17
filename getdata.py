from pymavlink import mavutil

# Connect to the MAVLink system
connection = mavutil.mavlink_connection('udp:127.0.0.1:14550')  # Adjust for your MAVLRS setup

# Wait for the heartbeat
print("Waiting for heartbeat...")
connection.wait_heartbeat()
print("Heartbeat received!")

while True:
    # Fetch GPS data
    gps_msg = connection.recv_match(type='GPS_RAW_INT', blocking=True)
    if gps_msg:
        latitude = gps_msg.lat / 1e7  # Convert to decimal degrees
        longitude = gps_msg.lon / 1e7
        gps_altitude = gps_msg.alt / 1000  # Convert to meters
        print(f"GPS: Lat={latitude}, Lon={longitude}, Alt={gps_altitude}m")

    # Fetch Rangefinder data
    rangefinder_msg = connection.recv_match(type='RANGEFINDER', blocking=True)
    if rangefinder_msg:
        rangefinder_distance = rangefinder_msg.distance  # In meters
        print(f"Rangefinder: {rangefinder_distance}m")

    # Fetch Altitude data
    altitude_msg = connection.recv_match(type='VFR_HUD', blocking=True)
    if altitude_msg:
        altitude = altitude_msg.alt  # In meters
        print(f"Altitude: {altitude}m")
