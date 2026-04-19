import serial
import time

ser = serial.Serial('COM4', 9600, timeout=1)

for i in range(100):
    ser.write(b'real\n' )  # b'' for bytes
    time.sleep(1)

ser.close()