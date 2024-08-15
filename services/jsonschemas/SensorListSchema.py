import jsonschema

sensor_list_schema = {
    "type": "array",
    "items": {
        "type": "string"
    }
}


def validate_sensor_list(data):
    try:
        jsonschema.validate(data, sensor_list_schema)
    except jsonschema.exceptions.ValidationError as e:
        return False, e.message
    return True, None
