import logging

from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN

from homeassistant.core import callback
from .coordinator import SettingsCoordinator
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities) -> None:
    entities = []

    dolphin = hass.data[DOMAIN][config_entry.entry_id]
    for device in dolphin.devices:
        coordinator = SettingsCoordinator(hass, dolphin, device.device_name)
        hass.async_create_task(coordinator.async_request_refresh())
        entities.append(DolphinSwitch(hass=hass, coordinator=coordinator, api=dolphin, device=device.device_name))

    async_add_entities(entities)


class DolphinSwitch(CoordinatorEntity, SwitchEntity):

    def __init__(self, hass, coordinator, api, device):
        CoordinatorEntity.__init__(self, coordinator)
        self._hass = hass
        self._api = api
        self._device = device
        self._is_on = False
        self._coordinator = coordinator

    @property
    def unique_id(self):
        return self._device

    @property
    def name(self):
        return "Sabbath mode"

    @property
    def is_on(self):
        return self._is_on

    async def async_turn_on(self):
        await self._hass.async_add_executor_job(
            self._api.enable_shabbat, self._device)
        self._hass.async_create_task(self._coordinator.async_request_refresh())
        self._is_on = True

    async def async_turn_off(self):
        await self._hass.async_add_executor_job(
            self._api.disable_shabbat, self._device)
        self._hass.async_create_task(self._coordinator.async_request_refresh())
        self._is_on = False

    @property
    def icon(self):
        return "mdi:star-david"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        try:
            data = self._coordinator.data

            if data.shabbat == "0":
                self._is_on = False

            else:
                self._is_on = True

        except KeyError:
            return
        self.async_write_ha_state()
