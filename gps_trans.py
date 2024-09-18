import serial
import pynmea2

# NEO-6M GPS 모듈과 시리얼 통신 설정
gps_serial = serial.Serial(
    port='/dev/ttyAMA0',  # GPS 모듈이 연결된 시리얼 포트. 예: /dev/ttyS0
    baudrate=9600,
    timeout=1
)

# 지상국으로 데이터 전송을 위한 시리얼 통신 설정
ground_station_serial = serial.Serial(
    port='/dev/ttyAMA1',  # 지상국으로 데이터 전송을 위한 포트
    baudrate=115200,
    timeout=1
)

def send_data_to_ground_station(data):
    ground_station_serial.write(data.encode('utf-8'))

try:
    while True:
        line = gps_serial.readline().decode('ascii', errors='replace')
        if line.startswith('$GPGGA') or line.startswith('$GPRMC'):
            try:
                msg = pynmea2.parse(line)
                if isinstance(msg, pynmea2.GGA) or isinstance(msg, pynmea2.RMC):
                    latitude = msg.latitude
                    longitude = msg.longitude
                    lat_dir = msg.lat_dir
                    lon_dir = msg.lon_dir

                    if lat_dir == 'S':
                        latitude = -latitude
                    if lon_dir == 'W':
                        longitude = -longitude

                    data_to_send = f"latitude: {latitude}, longitude: {longitude}"
                    send_data_to_ground_station(data_to_send)
                    print(data_to_send)
            except pynmea2.ParseError as e:
                print(f"Parse error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    gps_serial.close()
    ground_station_serial.close()
