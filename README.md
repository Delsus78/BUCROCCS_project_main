![image_20240920-214400](https://github.com/user-attachments/assets/7cc400a9-6e4c-42ab-90c0-babceed3cc6b)

---

# BUCROCCS Main - Flask Application for Sensor Management and UDP Communication

This project is a Flask-based application that controls and monitors sensors, communicates with Arduino devices, and sends data to a UDP server. It provides APIs to interact with sensors, Arduino, and manage data transfer over UDP.

## Requirements

- Python 3.x
- Flask
- asyncio
- pyserial
- requests
- flasgger (for API documentation)
- jsonschema

### Python Libraries

To install the necessary libraries, run the following command:

```bash
pip install -r requirements.txt
```

Where `requirements.txt` includes:
```
Flask
Flasgger
asyncio
pyserial
requests
jsonschema
```

## Overview

This project provides a REST API for:
- Managing sensors data.
- Controlling a pump connected to an Arduino device.
- Sending sensor data to a UDP server.

The application also includes a swagger interface for exploring and interacting with the API.

### Main Components

1. **flask_main.py**
   - Entry point of the Flask application.
   - Exposes various API endpoints to interact with sensors and manage data.
   - Uses Swagger for API documentation.
   - Handles both sensor data and UDP communication.

2. **controllers/MainController.py**
   - Central controller that manages sensor data, configuration checks, and communication with the UDP server.
   - Orchestrates Arduino actions like starting/stopping the pump and managing light.
   - Uses asynchronous functions to ensure smooth, non-blocking data transmission.

3. **models/ArduinoModel.py**
   - Manages serial communication with the Arduino device.
   - Handles pump activation and deactivation based on sensor data.

4. **services/UdpClient.py**
   - Handles communication with a remote UDP server.
   - Sends and receives sensor data via the UDP protocol.
   - Uses asyncio to ensure asynchronous, non-blocking UDP communication.

5. **services/AutoReconnectService.py**
   - Service to automatically log into the network/internet in case of connection drops.
   - Implements retry logic to ensure reconnection.

6. **services/ConfigurationsCheckerService.py**
   - Validates the sensor data against pre-defined thresholds.
   - Checks whether the pump and light need to be activated or deactivated based on the current sensor values.

7. **views/ConsoleView.py**
   - Provides console-based feedback and logs.
   - Displays real-time information about sensor data, pump state, and UDP messages.

### API Endpoints

- **`/api/sensors [GET]`**
  - Retrieves the list of sensors and their data.

- **`/api/sensors [POST]`**
  - Sets the list of sensors with new data. Requires a valid sensor list in the request body.

- **`/api/udp/start [POST]`**
  - Starts the UDP communication with the server.

- **`/api/udp/stop [POST]`**
  - Stops the UDP communication with the server.

- **`/api/udp/send [POST]`**
  - Sends sensor data to the UDP server.

- **`/api/arduino/pump [POST]`**
  - Starts or stops the pump connected to the Arduino.

### How to Run

1. Install dependencies using `pip`:

```bash
pip install -r requirements.txt
```

2. Run the Flask server using the following command:

```bash
python flask_main.py --start <arduino_port>
```

Replace `<arduino_port>` with your Arduino's serial port (e.g., `COM4` for Windows, `/dev/ttyUSB0` for Linux).

3. Open a web browser and navigate to `http://127.0.0.1:5000/apidocs` to view the Swagger API documentation and test the API endpoints.

### Example Usage

- **Start the Flask server:**

```bash
python flask_main.py --start COM4
```

- **Send sensor data to the UDP server:**

```bash
curl -X POST http://127.0.0.1:5000/api/udp/send -H "Content-Type: application/json" -d '{"id": "sensor_1", "data": {"temperature": 22.5, "humidity": 55}}'
```

### Folder Structure

- **controllers/**: Contains the main logic for handling API requests and controlling sensors.
- **models/**: Holds the Arduino communication model.
- **services/**: Contains helper services for UDP communication, Arduino helpers, and configuration checks.
- **views/**: Manages the display of information in the console.

## Extending the System

- You can modify `ArduinoModel.py` to add new hardware controls or handle more sensors.
- Customize `UdpClient.py` to change the target server or modify the UDP communication protocol.
- Expand the API by adding new routes in `flask_main.py` for additional functionalities.

---
