class ConfigurationsCheckerService:
    def __init__(self):
        pass

    @staticmethod
    def is_moistureValid(moisture_value, configs, pump_state, is_pump_activable) -> int:
        if moisture_value <= configs["moisture"].get("min") and not pump_state and is_pump_activable:
            return 1
        elif moisture_value >= configs["moisture"].get("max") and pump_state:
            return -1
        else:
            return 0

    @staticmethod
    def is_LightValid(light_value, configs, light_state) -> int:
        if light_state and light_value <= configs["light"].get("min"):
            return 0
        elif not light_state and light_value <= configs["light"].get("min"):
            return 1
        else:
            return -1
