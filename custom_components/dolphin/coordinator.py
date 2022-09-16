from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant
from .const import UPDATE_INTERVAL
import logging

_LOGGER = logging.getLogger(__name__)


class ClimateCoordinator(DataUpdateCoordinator):

    def __init__(self, hass: HomeAssistant, api, device) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="ClimateCoordinator",
            update_interval=UPDATE_INTERVAL,
        )
        self._api = api
        self._device = device
        self._hass = hass

    async def _async_update_data(self):
        """Fetch data from the API endpoint."""

        try:
            return await self._hass.async_add_executor_job(
                self._api.get_main_screen_data, self._device)

        except Exception as exceptioe:
            raise UpdateFailed(f"Error communicating with API: {exceptioe}") from exceptioe


class EnergyCoordinator(DataUpdateCoordinator):

    def __init__(self, hass: HomeAssistant, api, device) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="EnergyCoordinator",
            update_interval=UPDATE_INTERVAL,
        )
        self._api = api
        self._device = device
        self._hass = hass

    async def _async_update_data(self):
        """Fetch data from the API endpoint."""

        try:
            return await self._hass.async_add_executor_job(
                self._api.get_energy, self._device)

        except Exception as exceptioe:
            raise UpdateFailed(f"Error communicating with API: {exceptioe}") from exceptioe


class SettingsCoordinator(DataUpdateCoordinator):

    def __init__(self, hass: HomeAssistant, api, device) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="SettingsCoordinator",
            update_interval=UPDATE_INTERVAL,
        )
        self._api = api
        self._device = device
        self._hass = hass

    async def _async_update_data(self):
        """Fetch data from the API endpoint."""

        try:
            return await self._hass.async_add_executor_job(
                self._api.get_settings, self._device)

        except Exception as exceptioe:
            raise UpdateFailed(f"Error communicating with API: {exceptioe}") from exceptioe
