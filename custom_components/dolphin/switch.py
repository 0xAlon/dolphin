import logging
from typing import Callable, List
from homeassistant.components.switch import SwitchEntity
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
    """Set up Dolphin switch based on a config entry."""
    coordinator: UpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    switches = []

    for device in coordinator.data.keys():
        switches.append(ShabbatSwitch(hass=hass, coordinator=coordinator, device=device))
        switches.append(FixedTemperature(hass=hass, coordinator=coordinator, device=device))
        for switch in range(1, 7):
            switches.append(DropSwitch(hass=hass, coordinator=coordinator, index=switch, device=device))

    async_add_entities(switches)


class DropSwitch(CoordinatorEntity, SwitchEntity):

    def __init__(self, hass, coordinator, index, device):
        CoordinatorEntity.__init__(self, coordinator)
        self._hass = hass
        self._id = index
        self._coordinator = coordinator
        self._device = device
        self._is_on = False
        self.entity_id = async_generate_entity_id(DOMAIN + ".{}", None or f"{device}_drop{index}", hass=hass)

    @property
    def unique_id(self):
        return self.entity_id

    @property
    def name(self):
        if self._coordinator.data[self._device].showerTemperature != None:
            showerTemperature = self._coordinator.data[self._device].showerTemperature[self._id - 1]['temp'] if len(
                self._coordinator.data[self._device].showerTemperature) > self._id - 1 else None
        else:
            showerTemperature = None
        return f"{self._id} Shower - {showerTemperature}°C" if self._id == 1 else f"{self._id} Showers - {showerTemperature}°C"

    @property
    def icon(self):
        return "mdi:shower"

    @property
    def available(self):
        """Return availability."""
        if self._coordinator.data[self._device].shabbat:
            return False
        if self._coordinator.data[self._device].power and not self._is_on:
            return False
        if self._coordinator.data[self._device].fixedTemperature:
            return False
        if self._coordinator.data[self._device].showerTemperature != None:
            if len(self._coordinator.data[self._device].showerTemperature) > self._id - 1:
                return True

        return False

    @property
    def is_on(self):
        if not self._coordinator.data[self._device].power:
            self._is_on = False
        return self._is_on

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                (DOMAIN, self._device)
            },
        )

    async def async_turn_on(self):

        current_temp = self._coordinator.data[self._device].temperature
        drop_temperature = self._coordinator.data[self._device].showerTemperature[self._id - 1]['temp']

        if current_temp <= drop_temperature and self._coordinator.data[self._device].power == False:
            await self._coordinator.dolphin.turnOnManually(self._coordinator.dolphin._user, drop_temperature,
                                                           self._device)
            self._is_on = True
            await self.coordinator.async_request_refresh()
            self.async_write_ha_state()

    async def async_turn_off(self):

        await self._coordinator.dolphin.turnOffManually(self._coordinator.dolphin._user, self._device)
        self._is_on = False
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()


class ShabbatSwitch(CoordinatorEntity, SwitchEntity):

    def __init__(self, hass, coordinator, device):
        CoordinatorEntity.__init__(self, coordinator)
        self._hass = hass
        self._coordinator = coordinator
        self._device = device
        self.entity_id = async_generate_entity_id(DOMAIN + ".{}", None or f"{device}_sabbath_mode", hass=hass)

    @property
    def unique_id(self):
        return self.entity_id

    @property
    def name(self):
        return "Sabbath mode"

    @property
    def icon(self):
        return "mdi:star-david"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                (DOMAIN, self._device)
            },
            name=self.name,
        )

    @property
    def is_on(self):
        return self._coordinator.data[self._device].shabbat

    async def async_turn_on(self):
        await self._coordinator.dolphin.enableShabbat(self._coordinator.dolphin._user, self._device)
        self._coordinator.data[self._device].shabbat = True
        self.async_write_ha_state()

    async def async_turn_off(self):
        await self._coordinator.dolphin.disableShabbat(self._coordinator.dolphin._user, self._device)
        self._coordinator.data[self._device].shabbat = False
        self.async_write_ha_state()


class FixedTemperature(CoordinatorEntity, SwitchEntity):

    def __init__(self, hass, coordinator, device):
        CoordinatorEntity.__init__(self, coordinator)
        self._hass = hass
        self._coordinator = coordinator
        self._device = device
        self.entity_id = async_generate_entity_id(DOMAIN + ".{}", None or f"{device}_fixed_temperature", hass=hass)

    @property
    def unique_id(self):
        return self.entity_id

    @property
    def name(self):
        return "Fixed temperature"

    @property
    def icon(self):
        return "mdi:home-thermometer-outline"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                (DOMAIN, self._device)
            },
            name=self.name,
        )

    @property
    def is_on(self):
        return self._coordinator.data[self._device].fixedTemperature

    async def async_turn_on(self):
        await self._coordinator.dolphin.turnOnFixedTemperature(self._coordinator.dolphin._user, self._device,
                                                               self._coordinator.data[self._device].targetTemperature)
        self._coordinator.data[self._device].fixedTemperature = True
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_turn_off(self):
        await self._coordinator.dolphin.turnOffFixedTemperature(self._coordinator.dolphin._user, self._device)
        self._coordinator.data[self._device].fixedTemperature = False
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()
