import logging
from typing import Any
from typing import Callable, List
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .coordinator import UpdateCoordinator
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN
from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
    ClimateEntity,
)
from homeassistant.const import TEMP_CELSIUS
from homeassistant.components.climate.const import HVACMode

OPERATION_LIST = [HVACMode.HEAT, HVACMode.OFF]

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
        switches.append(DolphinWaterHeater(hass=hass, coordinator=coordinator, device=device))

    async_add_entities(switches)


class DolphinWaterHeater(CoordinatorEntity, ClimateEntity):
    _attr_hvac_modes = OPERATION_LIST
    _attr_temperature_unit = TEMP_CELSIUS

    def __init__(self, hass, coordinator, device):
        CoordinatorEntity.__init__(self, coordinator)
        self._device = device
        self._hass = hass

        self._name = device

        self._unit = TEMP_CELSIUS
        self._current_temperature = None
        self._attr_target_temperature_step = 1

        self._attr_max_temp = 71
        self._attr_min_temp = 20

        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
        )

        self._attr_hvac_mode = HVACMode.OFF
        self._coordinator = coordinator

        self._name = [i for i in self._coordinator.user.device if i['deviceName'] == device][0]['nickname']
        if self._name == None:
            self._name = "Dolphin"

        self._available = True

    @property
    def name(self):
        """Return the device name."""
        return self._name

    @property
    def unique_id(self):
        return f"climate.{self._device.lower()}"

    @property
    def icon(self):
        return "mdi:water-boiler"

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def current_temperature(self):
        """Return the sensor temperature."""
        return self._coordinator.data[self._device].temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._coordinator.data[self._device].targetTemperature if self._coordinator.data[
            self._device].power else 0

    @property
    def target_temperature_step(self):
        return self._attr_target_temperature_step

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current operation."""
        return HVACMode.HEAT if self._coordinator.data[self._device].power else HVACMode.OFF

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return self._attr_min_temp

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return self._attr_max_temp

    @property
    def available(self):
        """Return availability."""
        return not self._coordinator.data[self._device].shabbat

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                (DOMAIN, self._device)
            },
            name=self.name,
        )

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set temperature."""

        if kwargs.get('temperature') >= self._coordinator.data[self._device].temperature:
            await self._coordinator.dolphin.turnOnManually(self._coordinator.dolphin._user,
                                                           kwargs.get('temperature'), self._device)
            if self._coordinator.data[self._device].fixedTemperature:
                await self._coordinator.dolphin.turnOnFixedTemperature(self._coordinator.dolphin._user, self._device,
                                                                       kwargs.get('temperature'))
        else:
            self._coordinator.data[self._device].targetTemperature = self._coordinator.data[self._device].temperature

        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode):
        """Set HVAC mode."""

        if hvac_mode == HVACMode.OFF and not self._coordinator.data[self._device].power:

            await self._coordinator.dolphin.turnOnManually(self._coordinator.dolphin._user, self._attr_max_temp,
                                                           self._device)
            await self.coordinator.async_request_refresh()
            self.async_write_ha_state()

        elif hvac_mode == HVACMode.OFF and self._coordinator.data[self._device].power:

            await self._coordinator.dolphin.turnOffManually(self._coordinator.dolphin._user, self._device)
            if self._coordinator.data[self._device].fixedTemperature:
                await self._coordinator.dolphin.turnOffFixedTemperature(self._coordinator.dolphin._user, self._device)
                self._coordinator.data[self._device].fixedTemperature = False
            await self.coordinator.async_request_refresh()
            self.async_write_ha_state()

        elif not self._coordinator.data[self._device].power:

            await self._coordinator.dolphin.turnOnManually(self._coordinator.dolphin._user, self._attr_max_temp,
                                                           self._device)
            await self.coordinator.async_request_refresh()
            self.async_write_ha_state()
