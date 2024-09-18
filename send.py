import serial
import time

# serial 포트와 통신 속도를 설정합니다.
ser = serial.Serial(
    port='/dev/ttyAMA1',       # 포트 이름을 자신의 환경에 맞게 변경하세요. 예: 'COM3', '/dev/ttyUSB0'
    baudrate=115200,     # 보드레이트(통신 속도)를 설정합니다.
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1          # 타임아웃을 설정합니다.
)

def send_data(data):
    if ser.is_open:
        # 데이터를 바이트 형식으로 인코딩하여 송신합니다.
        ser.write(data.encode())
        print(f"Sent: {data}")
    else:
        print("Serial port is not open")

try:
    while True:
        # 송신할 데이터를 입력받습니다.
        data_to_send = "hello raspberry pi!"
        send_data(data_to_send)
        time.sleep(1)  # 1초 대기
except KeyboardInterrupt:
    print("Serial communication terminated")
finally:
    ser.close()  # 프로그램 종료 시 serial 포트를 닫습니다.
