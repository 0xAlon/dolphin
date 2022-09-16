"""Adds support for generic thermostat units."""

import logging
from .const import DOMAIN
from typing import Any

from homeassistant.components.climate import (
    PLATFORM_SCHEMA,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
    ClimateEntity,
    ATTR_TEMPERATURE
)

from .coordinator import ClimateCoordinator
from homeassistant.const import TEMP_CELSIUS
from homeassistant.components.climate.const import HVACMode
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

OPERATION_LIST = [HVACMode.HEAT, HVACMode.OFF]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add water heater entities for a config entry."""
    entities = []
    dolphin = hass.data[DOMAIN][config_entry.entry_id]

    for device in dolphin.devices:
        coordinator = ClimateCoordinator(hass, dolphin, device.device_name)
        hass.async_create_task(coordinator.async_request_refresh())
        entities.append(DolphinWaterHeater(coordinator=coordinator, hass=hass, api=dolphin,
                                           device=device.device_name))

    async_add_entities(entities)


class DolphinWaterHeater(CoordinatorEntity, ClimateEntity):
    _attr_hvac_modes = OPERATION_LIST
    _attr_temperature_unit = TEMP_CELSIUS

    def __init__(self, coordinator: DataUpdateCoordinator, hass, api, device):
        CoordinatorEntity.__init__(self, coordinator)
        self._api = api
        self._device = device
        self._hass = hass
        self._name = device

        self._unit = TEMP_CELSIUS
        self._current_temperature = None
        self._attr_target_temperature = 20
        self._attr_target_temperature_step = 0.1

        self._attr_max_temp = 71
        self._attr_min_temp = 20

        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
        )

        self._attr_hvac_mode = HVACMode.OFF
        self._coordinator = coordinator

    @property
    def name(self):
        """Return the device name."""
        return self._name

    @property
    def unique_id(self):
        """Return the device id."""
        return self._device

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
        return self._current_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._attr_target_temperature

    @property
    def target_temperature_step(self):
        return self._attr_target_temperature_step

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current operation."""
        return self._attr_hvac_mode

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return self._attr_min_temp

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return self._attr_max_temp

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set temperature."""
        if kwargs.get('temperature') >= float(self._current_temperature):
            self._attr_target_temperature = kwargs.get('temperature')
            await self._hass.async_add_executor_job(
                self._api.turn_on_temperature, self._device, kwargs.get('temperature'))
        else:
            self._attr_target_temperature = float(self._current_temperature)
        self._hass.async_create_task(self._coordinator.async_request_refresh())

    async def async_set_hvac_mode(self, hvac_mode):
        """Set HVAC mode."""
        if hvac_mode == HVACMode.OFF and self._attr_hvac_mode == HVACMode.HEAT:
            await self._hass.async_add_executor_job(
                self._api.turn_off_manually, self._device)
            self._attr_hvac_mode = HVACMode.OFF
            self._attr_target_temperature = None
        elif hvac_mode == HVACMode.OFF and self._attr_hvac_mode == HVACMode.OFF:
            await self._hass.async_add_executor_job(
                self._api.turn_on_manually, self._device)
            self._attr_target_temperature = self._attr_max_temp
            self._attr_hvac_mode = HVACMode.HEAT
        elif hvac_mode == HVACMode.HEAT:
            await self._hass.async_add_executor_job(
                self._api.turn_on_manually, self._device)
            self._attr_hvac_mode = HVACMode.HEAT
            self._attr_target_temperature = self._attr_max_temp
        else:
            pass
        self._hass.async_create_task(self._coordinator.async_request_refresh())

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        try:
            data = self._coordinator.data

            if data is None:
                pass
            else:
                if data.power.lower() == "off":
                    self._attr_hvac_mode = HVACMode.OFF
                else:
                    self._attr_hvac_mode = HVACMode.HEAT

                self._current_temperature = data.temperature

                if data.target != "null":
                    self._attr_target_temperature = data.target
                else:
                    self._attr_target_temperature = self._current_temperature

        except KeyError:
            return
        self.async_write_ha_state()
