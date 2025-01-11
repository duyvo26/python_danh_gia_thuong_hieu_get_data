import serial
import time
from app.config import settings


def reset_wifi():
    SER = serial.Serial(
        settings.SERIAL_PORT,
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0.5,
        writeTimeout=0,
    )

    print("ON")
    SER.setDTR(False)
    time.sleep(0.1)
    SER.setDTR(True)
    time.sleep(0.1)
    print("END")
