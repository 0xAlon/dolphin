import logging

from .const import DOMAIN

from homeassistant.core import callback
from .coordinator import EnergyCoordinator
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities) -> None:
    entities = []

    dolphin = hass.data[DOMAIN][config_entry.entry_id]

    for device in dolphin.devices:
        if await hass.async_add_executor_job(dolphin.is_energy_meter, device.device_name):
            coordinator = EnergyCoordinator(hass, dolphin, device.device_name)
            # hass.async_create_task(coordinator.async_request_refresh())
            entities.append(DolphinPower(hass=hass, api=dolphin, coordinator=coordinator, device=device.device_name))

    async_add_entities(entities)


class DolphinPower(CoordinatorEntity, SensorEntity):

    def __init__(self, hass, api, coordinator: DataUpdateCoordinator, device):
        CoordinatorEntity.__init__(self, coordinator)
        self._hass = hass
        self._api = api
        self._device = hass
        self._current = 0
        self._device = device
        self._unit_of_measurement = "A"
        self._state_class = "current"
        self._coordinator = coordinator

    @property
    def entity_id(self):
        return f"sensor.dolphin_{self._device.lower()}"

    @property
    def name(self):
        return "Electric current"

    @property
    def icon(self):
        return "mdi:lightning-bolt"

    @property
    def state(self):
        return self._current

    def get_coordinator(self):
        return self._coordinator

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        try:
            data = self._coordinator.data

            if data is None:
                pass
            else:
                self._current = data.energy

        except KeyError:
            return
        self.async_write_ha_state()
