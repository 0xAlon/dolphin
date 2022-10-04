from xmlrpc.client import Boolean
import requests
from .user import User
from .device import Device, Data, Energy, Settings


class dolphinAPI:
    ENDPOINT = "https://api.dolphinboiler.com"

    def __init__(self, email: str = None, password: str = None) -> None:
        self._session = requests.Session()
        self._user = self._get_access_token(email=email, password=password)
        self.devices = self._get_devices()

    @staticmethod
    def _get_access_token(email: str, password: str) -> User:
        payload = {
            "email": email,
            "password": password,
        }

        response = requests.post(f"{dolphinAPI.ENDPOINT}/HA/V1/getAPIkey.php", data=payload)

        if response.content.decode() == "failed":
            raise Exception(response['Error'])

        return User(response.content.decode(), email)

    def _get_devices(self) -> list[Device]:
        payload = {
            "email": self._user.email,
            "API_Key": self._user.access_key,

        }

        response = requests.post(f"{dolphinAPI.ENDPOINT}/HA/V1//getDevices.php", data=payload).json()

        return [
            Device(
                device["deviceName"],
                device["nickname"]
            )
            for device in response
        ]

    def get_main_screen_data(self, device: Device):
        payload = {
            "deviceName": device,
            "email": self._user.email,
            "API_Key": self._user.access_key,

        }

        response = requests.post(f"{dolphinAPI.ENDPOINT}/HA/V1/getMainScreenData.php", data=payload).json()

        try:
            if response["Error"]:
                return None
        except KeyError:

            if 'Shabbat' in response:
                return Data(
                    power=response["Power"],
                    temperature=response["Temperature"],
                    target=response["targetTemperature"],
                    shower=response["showerTemperature"],
                    shabbat=False,
                )
            else:
                return Data(
                    power=response["Power"],
                    temperature=response["Temperature"],
                    target=response["targetTemperature"],
                    shower=response["showerTemperature"],
                    shabbat=True,
                )

    def turn_on_manually(self, device: Device) -> None:
        payload = {
            "deviceName": device,
            "temperature": 71,
            "email": self._user.email,
            "API_Key": self._user.access_key,

        }

        requests.post(f"{dolphinAPI.ENDPOINT}/HA/V1/turnOnManually.php", data=payload)

    def turn_off_manually(self, device: Device) -> None:
        payload = {
            "deviceName": device,
            "email": self._user.email,
            "API_Key": self._user.access_key,

        }

        requests.post(f"{dolphinAPI.ENDPOINT}/HA/V1/turnOffManually.php", data=payload)

    def turn_on_temperature(self, device: Device, temperature: float) -> None:
        payload = {
            "deviceName": device,
            "temperature": temperature,
            "email": self._user.email,
            "API_Key": self._user.access_key,

        }

        requests.post(f"{dolphinAPI.ENDPOINT}/HA/V1/turnOnManually.php", data=payload)

    def enable_shabbat(self, device: Device):
        payload = {
            "deviceName": device,
            "email": self._user.email,
            "API_Key": self._user.access_key,

        }

        requests.post(f"{dolphinAPI.ENDPOINT}/HA/V1/enableShabbat.php", data=payload)

    def disable_shabbat(self, device: Device):
        payload = {
            "deviceName": device,
            "email": self._user.email,
            "API_Key": self._user.access_key,

        }

        requests.post(f"{dolphinAPI.ENDPOINT}/HA/V1/disableShabbat.php", data=payload)

    @staticmethod
    def validate_user(email: str, password: str) -> bool:
        payload = {
            "email": email,
            "password": password,

        }

        response = requests.post(f"{dolphinAPI.ENDPOINT}/HA/V1/getAPIkey.php", data=payload)

        if response.content.decode() == "failed":
            return False
        return True

    def get_energy(self, device: Device):
        payload = {
            "deviceName": device,
            "email": self._user.email,
            "API_Key": self._user.access_key,

        }

        response = requests.post(f"{dolphinAPI.ENDPOINT}/HA/V1/getEnergy.php", data=payload).json()

        try:
            if response["Error"]:
                return None
        except KeyError:
            return Energy(energy=response["energy"])

    def get_settings(self, device: Device) -> Settings:

        payload = {
            "deviceName": device,
            "email": self._user.email,
            "API_Key": self._user.access_key,

        }

        response = requests.post(f"{dolphinAPI.ENDPOINT}/HA/V1/getSettings.php", data=payload).json()

        return Settings(shabbat=response["isShabbatEnabled"], fixed_temperature=response["isFixedTemperatureEnabled"])

    def is_energy_meter(self, device) -> Boolean:

        payload = {
            "deviceName": device,
            "email": self._user.email,
            "API_Key": self._user.access_key,

        }

        response = requests.post(f"{dolphinAPI.ENDPOINT}/HA/V1/isEnergyMeter.php", data=payload).json()

        return True if response['isEnergyMeter'] == '1' else False
