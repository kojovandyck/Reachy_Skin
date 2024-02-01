import os
import numpy as np
import serial
from queue import Queue
from threading import Thread

class ReadLine:
    def __init__(self, s):
        self.buf = bytearray()
        self.s = s

    def readline(self):
        terminator = b"\n"
        while True:
            i = self.buf.find(terminator)
            if i >= 0:
                r = self.buf[:i+1]
                self.buf = self.buf[i+1:]
                return r
            data = self.s.read(2048)
            if not data:
                continue
            self.buf.extend(data)

class TactileSkin:
    def __init__(self, serialPort, serialBaud):
        self.port = serialPort
        self.baud = serialBaud
        self.serialConnection = None
        self.reader = None
        self.thread = None
        self.data_queue = Queue()

    def connect_serial(self):
        try:
            self.serialConnection = serial.Serial(self.port, self.baud, timeout=1)
            print(f"Connected to {self.port} at {self.baud} BAUD.")
            self.reader = ReadLine(self.serialConnection)
        except serial.SerialException:
            print(f"Failed to connect with {self.port} at {self.baud} BAUD.")

    def start_reading(self):
        if not self.serialConnection or not self.reader:
            print("Serial connection not established.")
            return
        self.thread = Thread(target=self._read_serial)
        self.thread.daemon = True
        self.thread.start()

    def _read_serial(self):
        while True:
            try:
                raw_data = self.reader.readline()
                if raw_data:
                    try:
                        raw_string = raw_data.decode('ascii', 'ignore')
                        self.data_queue.put(raw_string)
                    except UnicodeEncodeError:
                        pass
            except serial.SerialException:
                print("Error reading from serial.")
                break

    def read_data(self):
        if not self.data_queue.empty():
            return self.data_queue.get()
        return None

    def __str__(self):
        return 'TactileSkin'

# Example usage:
if __name__ == "__main__":
    port = "/dev/ttyUSB0"  # Example serial port
    baud_rate = 9600  # Example baud rate
    tactile_sensor = TactileSkin(port, baud_rate)
    tactile_sensor.connect_serial()
    tactile_sensor.start_reading()
    while True:
        data = tactile_sensor.read_data()
        if data:
            print("Received data:", data.strip())
