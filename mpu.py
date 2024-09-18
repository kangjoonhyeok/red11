import smbus

bus = smbus.SMBus(1)
address = 0x68  # MPU9250의 I2C 주소

try:
    bus.write_byte_data(address, 0x6B, 0x00)  # MPU9250 깨우기
    print("MPU9250 initialized successfully!")
except OSError as e:
    print("I2C communication error:", e)
