import json
from pymavlink import mavutil

class MavlinkHelper:
    def __init__(self, contype, port):
        try:
            self.connection_string = f"{contype}:{port}"
            self.connection = mavutil.mavlink_connection(self.connection_string)
            self.connection.wait_heartbeat()
            print("Heartbeat from system (system %u component %u)" % (self.connection.target_system, self.connection.target_component))
        except Exception as e:
            print(f"Failed to connect: {e}")
            raise

    def location(self, relative_alt=False):
        self.connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        if relative_alt:
            alt = self.connection.messages['GLOBAL_POSITION_INT'].relative_alt * 0.001
        else:
            alt = self.connection.messages['GLOBAL_POSITION_INT'].alt
        return {
            'lat': self.connection.messages['GPS_RAW_INT'].lat * 1.0e-7,
            'lon': self.connection.messages['GPS_RAW_INT'].lon * 1.0e-7,
            'alt': alt,
            'heading': self.connection.messages['VFR_HUD'].heading
        }

    def attitude(self):
        self.connection.recv_match(type='ATTITUDE', blocking=True)
        return {
            'roll': self.connection.messages['ATTITUDE'].roll,
            'pitch': self.connection.messages['ATTITUDE'].pitch,
            'yaw': self.connection.messages['ATTITUDE'].yaw
        }

    def system_uptime(self):
        self.connection.recv_match(type='SYSTEM_TIME', blocking=True)
        return self.connection.messages['SYSTEM_TIME'].time_unix_usec

    def battery_status(self):
        self.connection.recv_match(type='BATTERY_STATUS', blocking=True)
        return {
            'voltage': self.connection.messages['BATTERY_STATUS'].voltages[0],  # Example: first cell voltage
            'remaining_capacity': self.connection.messages['BATTERY_STATUS'].remaining
        }

    def gps_fix_type(self):
        self.connection.recv_match(type='GPS_RAW_INT', blocking=True)
        return self.connection.messages['GPS_RAW_INT'].fix_type

    def speed(self):
        self.connection.recv_match(type='VFR_HUD', blocking=True)
        return self.connection.messages['VFR_HUD'].airspeed, self.connection.messages['VFR_HUD'].groundspeed

def fetch_data(helper):
    # Initialize the data structure with default values
    data = {
        'Latitude': None,
        'Longitude': None,
        'Altitude': None,
        'Roll': None,
        'Pitch': None,
        'Yaw': None,
        'Airspeed': None,
        'Groundspeed': None,
        'System_Uptime': None,
        'Battery_Remaining_Capacity': None,
        'GPS_Fix_Type': None
    }
    
    try:
        # Attempt to fetch location, attitude, system uptime, battery status, GPS fix type, and speed
        location_data = helper.location(relative_alt=True)
        attitude_data = helper.attitude()
        system_uptime = helper.system_uptime()
        battery_status = helper.battery_status()
        gps_fix_type = helper.gps_fix_type()
        airspeed, groundspeed = helper.speed()

        # Update the data dictionary with actual values
        data.update({
            'Latitude': location_data['lat'],
            'Longitude': location_data['lon'],
            'Altitude': location_data['alt'],
            'Roll': attitude_data['roll'],
            'Pitch': attitude_data['pitch'],
            'Yaw': attitude_data['yaw'],
            'Airspeed': airspeed,
            'Groundspeed': groundspeed,
            'System_Uptime': system_uptime,
            'Battery_Remaining_Capacity': battery_status['remaining_capacity'],
            'GPS_Fix_Type': gps_fix_type
        })
    except Exception as e:
        print(f"Error fetching data: {e}")
        # No need to change 'data', it's already initialized with None values

    return data  # Return the data dictionary regardless of success or failure

# Example usage
contype = "tcp"
port = "127.0.0.1:5763"
helper = MavlinkHelper(contype, port)
data = fetch_data(helper)
print(json.dumps(data, indent=4))


# TODO 

# Ek olarak yer kontrol istasyonunun koordinatlarına göre İHA ile olan mesafe hesaplanacak (ESP32 ile GPS modülü ve serial port kullanılablir)
# Hava durumu api kullanılacak
# Rota tamamlama yüzdesi eklenecek
# Uçuş süresi eklenecek
 
