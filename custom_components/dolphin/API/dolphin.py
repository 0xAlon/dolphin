import socket
from typing import Any
import aiohttp
from yarl import URL
import asyncio
import ssl
import certifi
import json
import logging
from .models import User, Device

_LOGGER = logging.getLogger(__name__)


class Dolphin:
    """Main class for handling connections with Dolphin."""

    host: str = "api.dolphinboiler.com"
    request_timeout: float = 10.0
    session: aiohttp.client.ClientSession | None = None
    _client: aiohttp.ClientWebSocketResponse | None = None
    _close_session: bool = False
    _device: dict[str, Device] | None = None
    _user: User | None = None

    def __init__(self):
        self.ssl_context = None
        self._close_session = True

    async def create_ssl_context(self):
        """Create the SSL context asynchronously."""
        loop = asyncio.get_event_loop()
        self.ssl_context = await loop.run_in_executor(None, ssl.create_default_context, cafile=certifi.where())

    async def request(self, uri: str = "", method: str = "POST", data: dict[str, Any] | None = None) -> Any:
        url = URL.build(scheme="https", host=self.host, path=uri)

        if self.session is None:
            conn = aiohttp.TCPConnector(ssl=self.ssl_context)
            self.session = aiohttp.ClientSession(connector=conn)

        try:
            response = await self.session.request(method, url, data=data)
            response = await response.text("UTF-8")

            if "getAPIkey" not in url.path:
                return json.loads(response)
            return response

        except asyncio.TimeoutError as exception:
            _LOGGER.error(f"Timeout error while requesting {uri}: {exception}")
        except (aiohttp.ClientError, socket.gaierror) as exception:
            _LOGGER.error(f"Client error while requesting {uri}: {exception}")
        return None

    async def async_setup(self):
        """Set up the Dolphin integration."""
        await self.create_ssl_context()

    async def update(self, user: User) -> Device:
        for device in user.device:

            data = {
                "deviceName": device['deviceName'],
                "email": user.email,
                "API_Key": user.api,
            }
            if not (data := await self.request("/HA/V1/getMainScreenData.php", "POST", data)):
                pass

            if self._device is None:
                self._device = {device['deviceName']: Device(data)}
            elif device['deviceName'] not in self._device:
                self._device.update({device['deviceName']: Device(data)})
            else:
                self._device[device['deviceName']] = self._device[device['deviceName']].update_from_dict(data)

        return self._device

    async def getAPIKey(self, user: User, password: str) -> User:
        data = {
            "email": user.email,
            "password": password,
        }
        if not (data := await self.request("/HA/V1/getAPIkey.php", "POST", data)):
            pass

        if self._user is None:
            self._user = User(data)

        return self._user

    async def getDevices(self, user: User) -> User:
        data = {
            "email": user.email,
            "API_Key": user.api,
        }
        if not (data := await self.request("/HA/V1//getDevices.php", "POST", data)):
            pass

        self._user.update_from_dict(data)

        return self._user

    async def turnOnManually(self, user: User, temperature: str, deviceName: str):
        data = {
            "deviceName": deviceName,
            "temperature": temperature,
            "email": user.email,
            "API_Key": user.api,
        }

        if not (data := await self.request("/HA/V1/turnOnManually.php", "POST", data)):
            pass

    async def turnOffManually(self, user: User, deviceName: str):
        data = {
            "deviceName": deviceName,
            "email": user.email,
            "API_Key": user.api,
        }

        if not (data := await self.request("/HA/V1/turnOffManually.php", "POST", data)):
            pass

    async def enableShabbat(self, user: User, deviceName: str):
        data = {
            "deviceName": deviceName,
            "email": user.email,
            "API_Key": user.api,
        }

        if not (data := await self.request("/HA/V1/enableShabbat.php", "POST", data)):
            pass

    async def disableShabbat(self, user: User, deviceName: str):
        data = {
            "deviceName": deviceName,
            "email": user.email,
            "API_Key": user.api,
        }

        if not (data := await self.request("/HA/V1/disableShabbat.php", "POST", data)):
            pass

    async def isEnergyMeter(self, user: User, deviceName: str):
        data = {
            "deviceName": deviceName,
            "email": user.email,
            "API_Key": user.api,
        }

        if not (data := await self.request("/HA/V1/isEnergyMeter.php", "POST", data)):
            return 0
        return data['isEnergyMeter']

    async def turnOnFixedTemperature(self, user: User, deviceName: str, temperature: str):
        data = {
            "deviceName": deviceName,
            "temperature": temperature,
            "email": user.email,
            "API_Key": user.api,
        }

        if not (data := await self.request("/HA/V1/setFixedTemperature.php", "POST", data)):
            pass

    async def turnOffFixedTemperature(self, user: User, deviceName: str):
        data = {
            "deviceName": deviceName,
            "email": user.email,
            "API_Key": user.api,
        }

        if not (data := await self.request("/HA/V1/turnOffFixedTemperature.php", "POST", data)):
            pass

    async def disconnect(self) -> None:
        """Disconnect from the WebSocket of a Dolphin device."""
        if not self._client or not self.connected:
            return

        await self._client.close()

    async def close(self) -> None:
        """Close open client session and resources."""
        if self.session:
            await self.session.close()
        self.session = None
        _LOGGER.info("Session closed successfully")

    async def __aenter__(self):
        """Async enter."""
        return self

    async def __aexit__(self, *_exc_info: Any) -> None:
        """Async exit."""
        await self.close()
