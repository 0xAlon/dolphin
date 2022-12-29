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

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)

    async with Dolphin() as dolphin:
        user = User
        user.email = username
        user = await dolphin.getAPIKey(user, password)
        user = await dolphin.getDevices(user)

        coordinator = UpdateCoordinator(hass, dolphin, user)
        await coordinator.async_refresh()

        if not coordinator.last_update_success:
            raise ConfigEntryNotReady

        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = coordinator

        # Set up all platforms for this device/entry.
        for platform in PLATFORMS:
            hass.async_create_task(
                hass.config_entries.async_forward_entry_setup(entry, platform)
            )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Dolphin config entry."""

    # Unload entities for this entry/device.
    await asyncio.gather(
        *(
            hass.config_entries.async_forward_entry_unload(entry, component)
            for component in PLATFORMS
        )
    )

    # Cleanup
    del hass.data[DOMAIN][entry.entry_id]
    if not hass.data[DOMAIN]:
        del hass.data[DOMAIN]

    return True
