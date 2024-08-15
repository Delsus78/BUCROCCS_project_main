class ConfigurationsCheckerService:
    def __init__(self):
        pass

    def is_moistureValid(self, moistureValue, configs, pump_cache_state):
        if moistureValue <= configs["moisture"].get("min") and pump_cache_state is False:
            return True
        elif moistureValue >= configs["moisture"].get("stop") and pump_cache_state:
            return False

    def is_LightValid(self, lightValue, configs):
        return lightValue <= configs["light"].get("min")
