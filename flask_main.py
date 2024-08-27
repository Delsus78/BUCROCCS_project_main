import asyncio
import json
import sys

import flask
from flasgger import Swagger
from controllers.MainController import MainController
from services.AutoReconnectService import AutoReconnectService
from services.jsonschemas.SensorListSchema import validate_sensor_list

app = flask.Flask(__name__)
swagger = Swagger(app)
controller = MainController(server_ip='udpserver.bu.ac.th', server_port=5005, arduino_port=sys.argv[2] if len(sys.argv) > 2 else 'COM4')
#controller = MainController(server_ip='udpserver.bu.ac.th', server_port=5005)


@app.route('/')
def index():
    return controller.view.index()


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


@app.route('/api/udp/send', methods=['POST'])
def send_udp():
    """
    Send Data to UDP server
    ---
    tags:
      - UDP
    parameters:
      - in: body
        name: body
        schema:
            type: object
            properties:
                id:
                    type: string
                data:
                    type: object
    responses:
        200:
            description: Data sent
    """

    controller.retrieve_udp_data(
        command='SET',
        id_str=flask.request.json.get('id'),
        json_data=flask.request.json.get('data')).close()

    return 'Data sent'


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
        asyncio.run(controller.start_pump(start, configs))
        return 'Pump started'
    return 'Controller not started !'


@app.route('/api/loginTointernet', methods=['POST'])
def loginTointernet():
    """
    login to internet
    ---
    tags:
      - API
    responses:
        200:
            description: Logged in
    """
    asyncio.run(AutoReconnectService().login())
    return 'Reconnected !'


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--start':
        controller.start()
    else:
        app.run()
    controller.close()
