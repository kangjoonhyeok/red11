import time
import serial
import base64
import cv2
from mpu9250_jmdev.registers import *
from mpu9250_jmdev.mpu_9250 import MPU9250

# Initialize MPU9250 instance
mpu = MPU9250(
    address_ak=AK8963_ADDRESS,
    address_mpu_master=MPU9050_ADDRESS_68,  # In case the MPU9250 is connected to another I2C device
    address_mpu_slave=None,
    bus=1,
    gfs=GFS_1000,
    afs=AFS_8G,
    mfs=AK8963_BIT_16,
    mode=AK8963_MODE_C100HZ)

# Configure the MPU9250
mpu.configure()

# Initialize serial communication
serial_port = '/dev/ttyAMA1'
baud_rate = 115200
ser = serial.Serial(serial_port, baud_rate, timeout=1)

def capture_image():
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Cannot open camera.")
        return None
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("Cannot capture image.")
        return None
    
    # Encode image to JPEG format
    ret, jpeg = cv2.imencode('.jpg', frame)
    
    if not ret:
        print("Cannot encode image to JPEG.")
        return None
    
    return jpeg.tobytes()

def send_image_data(image_data):
    # Encode to Base64
    encoded_data = base64.b64encode(image_data)
    
    # Get data size
    data_size = len(encoded_data)
    
    # Send data in chunks
    chunk_size = 1024  # Chunk size
    for i in range(0, data_size, chunk_size):
        chunk = encoded_data[i:i+chunk_size]
        ser.write(chunk)
        print(chunk)
        
        time.sleep(0.32)  # Wait between chunks

def send_accel_data():
    accel_data = mpu.readAccelerometerMaster()
    data = f"{accel_data[0]:.2f},{accel_data[1]:.2f},{accel_data[2]:.2f}\n"
    ser.write(data.encode())
    print(data)

try:
    while True:
        # Capture and send image data
        image_data = capture_image()
        
        if image_data is not None:
            send_image_data(image_data)
            print("Image sent!")
        
        # Wait for 5 seconds, sending accelerometer data every second
        for _ in range(10):
            send_accel_data()
            time.sleep(1)

except KeyboardInterrupt:
    print("Program terminated")

finally:
    # Release resources
    ser.close()
