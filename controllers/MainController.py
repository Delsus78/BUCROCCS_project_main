import asyncio

from models.ArduinoModel import ArduinoModel
from services.ArduinoHelpers import transform_data_to_match_client_interpretation
from services.ConfigurationsCheckerService import ConfigurationsCheckerService
from services.TimeHelpers import get_actual_hour, get_actual_day, get_actual_day_from_int
from views.ConsoleView import ConsoleView
from services.UdpClient import UdpClient

FARM2000_SENSOR_LIST = "farm2000_sensor_list"
FARM2000_CONFIGURATION = "farm2000_configs"
FARM2000_PUMP_OPEN_TIME = 3
FARM2000_PUMP_INTERVAL = 10


class MainController:
    def __init__(self, server_ip, server_port):
        self.model = ArduinoModel()
        self.view = ConsoleView()
        self.configurationsCheckerService = ConfigurationsCheckerService()
        self.udp_client = UdpClient(server_ip, server_port)
        self.loop = asyncio.get_event_loop()
        self.running = True

    def start(self):
        self.view.display_info("Starting MainController...")
        # Start the main loop in a non-blocking way
        self.loop.run_until_complete(self.main())
        print("MainController stopped")

    def stop(self):
        self.view.display_info("Stopping MainController...")
        self.running = False

    async def main(self):
        while self.running:
            self.view.display_info("[CONFIG] Checking parameters ...")
            await self.check_configuration_periodically()
            self.view.display_info("[DATA] Actualising data ...")
            await self.send_data_periodically()
            await asyncio.sleep(3)

    async def send_data_periodically(self):
        data = self.get_data_from_sensors()
        if data:
            data_transformed = transform_data_to_match_client_interpretation(data)
            id_str = f"farm2000_" + str(get_actual_day())
            actual_udp_data = await self.get_udp_server_data_of_the_day()

            if 'Error' in actual_udp_data.keys():
                print("[ERROR] Error while retrieving data from UDP server, retrying...")
                return

            if get_actual_hour() in actual_udp_data:
                actual_udp_data[get_actual_hour()] = {
                    **actual_udp_data[get_actual_hour()], **data_transformed[get_actual_hour()]
                }
            else:
                actual_udp_data = {**actual_udp_data, **data_transformed}

            final_data_of_the_day = actual_udp_data
            await self.udp_client.retrieve_data(
                command="SET", id_str=id_str, json_data=final_data_of_the_day, view=self.view)
        else:
            self.view.display_info("No data retrieved from sensors, Skipping ...")

    async def check_configuration_periodically(self):
        configs = await self.get_configuration_data()
        if not configs:
            return

        hour = get_actual_hour()
        udp_data = await self.get_udp_server_data_of_the_day()

        if hour in udp_data:

            # MOISTURE
            moisture_val = udp_data[hour].get("MOISTURE")
            if self.configurationsCheckerService.is_moistureValid(moisture_val, configs, self.model.pump_cache_state):
                await self.start_pump(True)
            else:
                await self.start_pump(False)

            # LIGHT
            light_val = udp_data[hour].get("LIGHT")
            if self.configurationsCheckerService.is_LightValid(light_val, configs):
                await self.setLedInWhite()
            else:
                await self.setLedOff()

    def get_all_week_data(self):
        self.view.display_info("Getting all week data ...")
        all_week_data = []
        for i in range(7):
            day = get_actual_day_from_int(i)
            data = self.udp_client.retrieve_data(command="GET", id_str=f"farm2000_{day}")
            # map the data to the day
            all_week_data.append({day: data})

        return all_week_data

    def set_sensor_list(self, list_of_sensors):
        self.view.display_info("Setting sensors ...")
        self.udp_client.retrieve_data(command="SET", id_str=FARM2000_SENSOR_LIST, json_data=list_of_sensors,
                                      view=self.view)

    def get_sensor_list(self):
        self.view.display_info("Getting sensors ...")
        data = self.udp_client.retrieve_data(command="GET", id_str=FARM2000_SENSOR_LIST)
        return data

    def get_data_from_sensors(self):
        data = self.model.wait_for_serial_data()
        if data:
            self.view.display_data(data)
            return data
        return None

    async def get_udp_server_data_of_the_day(self):
        data = await self.udp_client.retrieve_data(command="GET", id_str=f"farm2000_{get_actual_day()}", view=self.view)
        return data

    async def get_configuration_data(self):
        data = await self.udp_client.retrieve_data(command="GET", id_str=FARM2000_CONFIGURATION, view=self.view)

        if 'Error' in data.keys():
            print("[CONFIG] Error while retrieving data from UDP server, retrying...")
            return

        if data and ('type' not in data.keys() or 'configuration' not in data.get('type')):
            print("[CONFIG] Wrong data retrieved from UDP server, got : ", data, ", retrying...")
            return {}

        if not data:
            data = {
                "type": "configuration",
                "moisture": {
                    "min": 30.0,
                    "stop": 40.0
                },
                "light": {
                    "min": 30.0,
                }
            }

            print("[CONFIG] creating new config file...")
            await self.udp_client.retrieve_data(command="SET", id_str=FARM2000_CONFIGURATION, json_data=data,
                                                view=self.view)

        return data

    async def start_pump(self, start):
        self.view.display_info("Starting pump ..." if start else "Stopping pump ...")
        await self.model.start_pump(start, FARM2000_PUMP_OPEN_TIME, FARM2000_PUMP_INTERVAL)

    async def setLedInWhite(self):
        self.view.display_info("Setting LED in white ...")
        await self.model.set_led_in_white()

    async def setLedOff(self):
        self.view.display_info("Turning LED off ...")
        await self.model.set_led_off()

    def close(self):
        print("[CLOSING] Closing MainController...")
        self.model.close()
        self.udp_client.close()
        self.running = False
