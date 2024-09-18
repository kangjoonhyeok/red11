import cv2
import time
import base64
import sys
import subprocess

def restart_program():
    print("프로그램을 재시작합니다.")
    subprocess.Popen([sys.executable] + sys.argv)
    ser.close()
    GPIO.cleanup()
    sys.exit()


#
#      공대선배 라즈베리파이썬 #8.5 떨림없는 서보모터 제어
#      youtube 바로가기: https://www.youtube.com/c/공대선배
#      서보모터가 떨리지 않게 방지하며 제어하기
#

import RPi.GPIO as GPIO     # 라즈베리파이 GPIO 관련 모듈을 불러옴
from time import sleep      #time 라이브러리의 sleep함수 사용

GPIO.setmode(GPIO.BCM)      # GPIO 핀들의 번호를 지정하는 규칙 설정

### 이부분은 아두이노 코딩의 setup()에 해당합니다
servo_pin1 = 12                   # 서보핀은 라즈베리파이 GPIO 12번핀으로 
servo_pin2 = 18

GPIO.setup(servo_pin1, GPIO.OUT)  # 서보핀을 출력으로 설정 
GPIO.setup(servo_pin2,GPIO.OUT)
servo1 = GPIO.PWM(servo_pin1, 50)  # 서보핀을 PWM 모드 50Hz로 사용
servo2 = GPIO.PWM(servo_pin2, 50)
servo1.start(0)  # 서보모터의 초기값을 0으로 설정
servo2.start(0)
servo_min_duty = 3               # 최소 듀티비를 3으로
servo_max_duty = 12              # 최대 듀티비를 12로

import serial
import threading

def serial_monitor():
    ser = serial.Serial('/dev/ttyAMA1', 115200, timeout=1)
    ser.flush()
    
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            if line == "Reset":
                restart_program()
            # 데이터를 받을 때 다른 동작 수행

# 별도의 스레드에서 시리얼 모니터링
monitor_thread = threading.Thread(target=serial_monitor)
monitor_thread.daemon = True
monitor_thread.start()



def set_servo_degree(servo_pin, servo, degree):    # 각도를 입력하면 듀티비를 알아서 설정해주는 함수
    # 각도는 최소0, 최대 180으로 설정
    if degree > 180:
        degree = 180
    elif degree < 0:
        degree = 0

    # 입력한 각도(degree)를 듀티비로 환산하는 식
    duty = servo_min_duty+(degree*(servo_max_duty-servo_min_duty)/180.0)
    # 환산한 듀티비를 서보모터에 전달
    GPIO.setup(servo_pin, GPIO.OUT)  # ★서보핀을 출력으로 설정 
    servo.ChangeDutyCycle(duty)
    sleep(0.3)                        # ★0.3초 쉼
    GPIO.setup(servo_pin, GPIO.IN)  # ★서보핀을 입력으로 설정 (더이상 움직이지 않음)

### 이부분은 아두이노 코딩의 loop()에 해당합니다
                                   # 이 try 안의 구문을 먼저 수행하고
### 이부분은 반드시 추가해주셔야 합니다.


# 시리얼 포트 설정
serial_port = '/dev/ttyAMA1'
baud_rate = 115200

# 시리얼 통신 설정
ser = serial.Serial(serial_port, baud_rate, timeout=1)

def capture_image():
    # 카메라 초기화
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        return None
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("이미지를 캡처할 수 없습니다.")
        return None
    
    # 이미지 크기 변경 (680x480)
    resized_frame = cv2.resize(frame, (680, 480))
    
    # JPEG 형식으로 이미지 인코딩
    ret, jpeg = cv2.imencode('.jpg', resized_frame)
    
    if not ret:
        print("이미지를 JPEG로 인코딩할 수 없습니다.")
        return None
    
    return jpeg.tobytes()

def send_image_data(image_data):
    # Base64 인코딩
    encoded_data = base64.b64encode(image_data)
    
    # 데이터 크기 전송
    data_size = len(encoded_data)
    
    # 청크 단위로 데이터 전송
    chunk_size = 1024  # 청크 크기
    for i in range(0, data_size, chunk_size):
        chunk = encoded_data[i:i+chunk_size]
        ser.write(chunk)
        print(chunk)
        
        time.sleep(0.24)  # 청크 간 잠시 대기
    ser.write(b'END\n')

try:
    
        image_data = capture_image()
        
        if image_data is not None:
            # 사진 데이터 전송
            send_image_data(image_data)
            print("전송 완료!")
        if ser.in_waiting > 0:
            signal = ser.readline().decode('utf-8').strip()
            if signal == "RESET":
                restart_program()  
        # 잠시 대기
        time.sleep(5)
        while True:
            set_servo_degree(servo_pin1,servo1,0)             # 서보모터의 각도를 0도로
            sleep(0.7)                        # 2초간 대기
            set_servo_degree(servo_pin2,servo2,0)
            sleep(0.7)
            set_servo_degree(servo_pin1,servo1,90)
            sleep(0.7)
            set_servo_degree(servo_pin2,servo2,90)
            sleep(0.7)
            set_servo_degree(servo_pin1,servo1,150)             # 서보모터의 각도를 0도로
            sleep(0.7)                        # 2초간 대기
            set_servo_degree(servo_pin2,servo2,150)
            sleep(0.7)
            set_servo_degree(servo_pin1,servo1,90)
            sleep(0.7)
            set_servo_degree(servo_pin2,servo2,90)
            sleep(0.7)

except KeyboardInterrupt:
    print("프로그램 종료")

finally:
    # 자원 해제
    ser.close()                             # try 구문이 종료되면
    GPIO.cleanup()                      # GPIO 핀들을 초기화