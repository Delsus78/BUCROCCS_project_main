import asyncio
import threading

import serial
import time
from services.ArduinoHelpers import parse_line, read_arduino_serial


class ArduinoModel:
    def __init__(self, port='COM4', baudrate=115200, timeout=1):
        self.serial_monitor = serial.Serial(port, baudrate, timeout=timeout)
        self.is_pump_activable = True
        self.lock = asyncio.Lock()
        time.sleep(2)  # Wait for the serial connection to initialize

    def set_pump_activable(self, value):
        self.is_pump_activable = value

    def wait_for_serial_data(self):
        if self.serial_monitor.in_waiting > 0:
            line = read_arduino_serial(self.serial_monitor)
            return parse_line(line)
        return {}

    def close(self):
        self.serial_monitor.close()

    async def start_pump(self, start, pump_open_time, pump_interval_time):
        if start:
            message = 'RELAY ON'
            self.is_pump_activable = False
            # start a thread to desactivate the pump after pump_open_time seconds
            threading.Timer(pump_open_time, lambda: asyncio.run(
                self.start_pump(False, pump_open_time, pump_interval_time))).start()

            # start a thread to set the pump activable again after pump_interval_time seconds
            threading.Timer(pump_interval_time, self.set_pump_activable, args=[True]).start()
        else:
            message = 'RELAY OFF'

        await self.writeInSerial(message)

    async def set_light(self, state):
        message = 'LIGHT ' + ('ON' if state else 'OFF')
        await self.writeInSerial(message)

    async def writeInSerial(self, message):
        async with self.lock:
            self.serial_monitor.write(message.encode())
            await asyncio.sleep(1.5)
