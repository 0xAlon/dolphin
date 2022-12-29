import logging
from typing import Callable, List
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .coordinator import UpdateCoordinator
from homeassistant.helpers.entity import DeviceInfo, async_generate_entity_id
from .const import (
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1


async def async_setup_entry(
        hass: HomeAssistantType,
        entry: ConfigEntry,
        async_add_entities: Callable[[List[Entity], bool], None],
) -> None:
    coordinator: UpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    switches = []

    for device in coordinator.data.keys():
        if await coordinator.dolphin.isEnergyMeter(coordinator.dolphin._user, device) == '1':
            switches.append(PowerSensor(hass=hass, coordinator=coordinator, device=device))

    async_add_entities(switches)


class PowerSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, hass, coordinator, device):
        CoordinatorEntity.__init__(self, coordinator)
        self._hass = hass
        self._device = device
        self._unit_of_measurement = "A"
        self._state_class = "current"
        self._coordinator = coordinator
        self.entity_id = async_generate_entity_id(DOMAIN + ".{}", None or f"{device}_electric_current", hass=hass)

    @property
    def unique_id(self):
        return self.entity_id

    @property
    def name(self):
        return "Electric current"

    @property
    def icon(self):
        return "mdi:lightning-bolt"

    @property
    def state(self):
        return self._coordinator.data[self._device].energy

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                (DOMAIN, self._device)
            },
            name=self.name,
        )
