import logging

from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN
from homeassistant.core import callback
from .coordinator import ClimateCoordinator
from homeassistant.helpers.update_coordinator import CoordinatorEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities) -> None:
    entities = []
    dolphin = hass.data[DOMAIN][config_entry.entry_id]

    for device in dolphin.devices:
        coordinator = ClimateCoordinator(hass, dolphin, device.device_name)
        # hass.async_create_task(coordinator.async_request_refresh())
        entities.append(ShabbatSwitch(hass=hass, coordinator=coordinator, api=dolphin, device=device.device_name))

        drops = await hass.async_add_executor_job(dolphin.get_main_screen_data, device.device_name)

        for index in range(1, 7):
            entities.append(DropSwitch(hass=hass, coordinator=coordinator, api=dolphin, device=device.device_name,
                                       drop=drops, index=index))

    async_add_entities(entities)


class DropSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, hass, coordinator, api, device, drop, index):
        CoordinatorEntity.__init__(self, coordinator)
        self._hass = hass
        self._api = api
        self._device = device
        self._id = index

        try:
            self._temp = drop.shower[index - 1]['temp']
        except:
            self._temp = None

        self._is_on = False
        self._coordinator = coordinator

        if self._temp is not None:
            self._available = True
        else:
            self._available = False

    @property
    def available(self):
        """Return availability."""
        return self._available

    @property
    def entity_id(self):
        return f"switch.dolphin_drop{self._id}_{self._device.lower()}"

    @property
    def name(self):
        return f"{self._id} Shower - {self._temp}°C" if self._id == 1 else f"{self._id} Showers - {self._temp}°C"

    @property
    def icon(self):
        return "mdi:shower"

    @property
    def is_on(self):
        return self._is_on

    async def async_turn_on(self):

        current_temp = self._hass.states.get(f"climate.dolphin_{self._device.lower()}").attributes[
            'current_temperature']
        if current_temp <= self._temp:
            await self._hass.async_add_executor_job(self._api.turn_on_temperature, self._device, self._temp)
            self._is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self):

        await self._hass.async_add_executor_job(
            self._api.turn_off_manually, self._device)
        self._is_on = False
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        try:
            data = self._coordinator.data
            if len(data.shower) >= self._id:
                temp = data.shower[self._id - 1]['temp']
                self._temp = temp
                self._available = True
            else:
                self._temp = None
                self._available = False

            if data.power.lower() == "off":
                self._is_on = False
                self.async_write_ha_state()

        except KeyError:
            return
        except AttributeError:
            return

        self.async_schedule_update_ha_state(True)
        self.async_write_ha_state()


class ShabbatSwitch(CoordinatorEntity, SwitchEntity):

    def __init__(self, hass, coordinator, api, device):
        CoordinatorEntity.__init__(self, coordinator)
        self._hass = hass
        self._api = api
        self._device = device
        self._is_on = False
        self._coordinator = coordinator

    @property
    def entity_id(self):
        return f"switch.dolphin_{self._device.lower()}"

    @property
    def name(self):
        return "Sabbath mode"

    @property
    def is_on(self):
        return self._is_on

    async def async_turn_on(self):
        await self._hass.async_add_executor_job(
            self._api.enable_shabbat, self._device)
        self._is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self):
        await self._hass.async_add_executor_job(
            self._api.disable_shabbat, self._device)
        self._is_on = False
        self.async_write_ha_state()

    @property
    def icon(self):
        return "mdi:star-david"

    @callback
    def _handle_coordinator_update(self) -> None:
        try:
            data = self._coordinator.data

            if data is None:
                pass
            else:
                if data.shabbat == True:
                    self._is_on = False
                    self.async_write_ha_state()
                else:
                    self._is_on = True
                    self.async_write_ha_state()
        except KeyError:
            return
