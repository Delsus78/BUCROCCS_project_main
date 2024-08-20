from services.TimeHelpers import get_actual_hour


def parse_line(line):
    data = line.split('|')
    data.pop()  # remove the last element which is an empty string

    parsed_data = []
    for i in range(len(data)):
        measures_data = data[i].split(';')
        measure_data = {}
        for j in range(len(measures_data)):
            key, value = measures_data[j].split(':')
            measure_data[key] = value
        parsed_data.append(measure_data)

    return parsed_data


def read_arduino_serial(serial_monitor):
    line = serial_monitor.readline().decode('utf-8').rstrip()

    if 'DHT22' in line or 'Initialized' in line:  # 'DHT22' in line
        print("[INIT] - {0}".format(line))
        line = read_arduino_serial(serial_monitor)

    return line


def transform_data_to_match_client_interpretation(data):
    response = {}
    for i in range(len(data)):

        # transform LIGHT data from 0-1023 to 0-100
        data[i]['LIGHT'] = str(int(int(data[i]['LIGHT']) * 100 / 1023))

        # transform MOISTURE data from 0-1023 to 0-100
        moisture_val = int(data[i]['MOISTURE'])

        data[i]['MOISTURE'] = \
            127 + (0.431 * moisture_val) + (-2.28 * pow(10, -3) * pow(moisture_val, 2)) \
            + (3.19 * pow(10, -6) * pow(moisture_val, 3)) + (-1.45 * pow(10, -9) * pow(moisture_val, 4))

        if int(data[i]['MOISTURE']) < 0 or int(data[i]['MOISTURE']) > 100:
            data[i]['MOISTURE'] = 0

        # transform to float the values
        data[i]['MOISTURE'] = float(data[i]['MOISTURE'])
        data[i]['LIGHT'] = float(data[i]['LIGHT'])
        data[i]['TEMPERATURE'] = float(data[i]['TEMPERATURE'])
        data[i]['HUMIDITY'] = float(data[i]['HUMIDITY'])
        data[i]['PUMPSTATE'] = int(data[i]['PUMPSTATE']) == 1
        data[i]['LIGHTSTATE'] = int(data[i]['LIGHTSTATE']) == 1

        # match with the actual hour as a key (i.e 12 : { 'MOISTURE': 100, 'LIGHT': 0 })
        response = {get_actual_hour(): data[i]}

        print("transforming data...")
    return response
