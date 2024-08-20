import json
import sys

import flask
from flasgger import Swagger
from controllers.MainController import MainController
from services.jsonschemas.SensorListSchema import validate_sensor_list

app = flask.Flask(__name__)
swagger = Swagger(app)
controller = MainController(
    server_ip='udpserver.bu.ac.th', server_port=5005, arduino_port=sys.argv[2] if len(sys.argv) > 2 else 'COM4')


@app.route('/')
def index():
    return controller.view.index()


@app.route('/api/sensors/data', methods=['GET'])
def get_sensors_data():
    """
    Get data from sensors stocked in the udp server
    ---
    tags:
      - Sensors
    responses:
        200:
            description: Data from sensors
    """
    data = controller.get_all_week_data()

    if data:
        return flask.jsonify(data)
    return 'No data from Sensors, try again later'


@app.route('/api/sensors', methods=['GET'])
def get_sensors():
    """
    Get data from sensors
    ---
    tags:
      - Sensors
    parameters:
      - in: body
        name: body
        schema:
            type: array
            items:
                type: string
    responses:
      200:
        description: Sensors set
      404:
        description: No sensors found
    """
    data = controller.get_sensor_list()

    if data:
        return flask.jsonify(json.loads(data))

    return 'No sensors found', 404


@app.route('/api/sensors', methods=['POST'])
def set_sensors():
    """
    Set data from sensors
    ---
    tags:
      - Sensors
    parameters:
      - in: body
        name: body
        schema:
            type: array
            items:
                type: string
    responses:
      200:
        description: Sensors set
      500:
        description: Error occurred while setting sensors
    """

    list_of_sensors = flask.request.json
    valid, error = validate_sensor_list(list_of_sensors)

    if valid is False:
        return 'Invalid sensor list : ' + error, 400

    controller.set_sensor_list(list_of_sensors)
    return flask.jsonify(list_of_sensors)


@app.route('/api/udp/start', methods=['POST'])
def start_udp():
    """
    Start sending data to UDP server
    ---
    tags:
      - UDP
    responses:
        200:
            description: UDP server started
    """
    controller.start()
    return 'UDP server started'


@app.route('/api/udp/stop', methods=['POST'])
def stop_udp():
    """
    Stop sending data to UDP server
    ---
    tags:
      - UDP
    responses:
        200:
            description: UDP server stopped
    """
    controller.stop()
    return 'UDP server stopped'


@app.route('/api/arduino/pump', methods=['POST'])
def pump():
    """
    Start the pump
    ---
    tags:
      - Arduino
    parameters:
      - in: body
        name: body
        schema:
            type: object
            properties:
                start:
                    type: boolean
    responses:
        200:
            description: Pump started
    """
    start = flask.request.json.get('start')
    if controller.running:
        configs = controller.get_configuration_data()
        await controller.start_pump(start, configs)
        return 'Pump started'
    return 'Controller not started !'


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--start':
        controller.start()
    else:
        app.run()
    controller.close()
