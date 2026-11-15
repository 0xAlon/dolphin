"""Dolphin integration."""

from .API.dolphin import Dolphin, User

from .const import (
    DOMAIN,
    PLATFORMS,
    CONF_PASSWORD,
    CONF_USERNAME,
)

import asyncio
from .coordinator import UpdateCoordinator
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)

    session = async_get_clientsession(hass)
    dolphin = Dolphin(session)
    user = User
    user.email = username
    user = await dolphin.getAPIKey(user, password)
    if not user.api:
        raise ConfigEntryNotReady("Could not get an API key from the Dolphin API")

    user = await dolphin.getDevices(user)
    if not user.device:
        raise ConfigEntryNotReady("Could not get the device list from the Dolphin API")

    coordinator = UpdateCoordinator(hass, entry, dolphin, user)
    # Raises ConfigEntryNotReady on failure, so Home Assistant retries setup.
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Dolphin config entry."""

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Cleanup
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)

    return unload_ok
