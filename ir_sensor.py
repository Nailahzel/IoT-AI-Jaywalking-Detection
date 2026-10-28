import serial
import time

class IRSensor:
    def __init__(self, port: str, baud: int = 9600):
        self.ser = serial.Serial(port, baudrate=baud, timeout=1)
        time.sleep(2)  # allow Arduino reset
        self.last_state = "NO_MOTION"

    def read_state(self) -> str:
        """Returns 'MOTION' or 'NO_MOTION'."""
        if self.ser.in_waiting:
            line = self.ser.readline().decode(errors="ignore").strip()
            if line in ("MOTION", "NO_MOTION"):
                self.last_state = line
        return self.last_state
