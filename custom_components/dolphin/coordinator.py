import logging
from .API.dolphin import Dolphin, User, Device

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    UPDATE_INTERVAL,
)

_LOGGER: logging.getLogger = logging.getLogger(__package__)


class UpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Dolphin data from single endpoint."""

    def __init__(
            self, hass: HomeAssistant, entry: ConfigEntry, dolphin: Dolphin, user: User):
        """Initialize global Dolphin data updater."""
        self.dolphin = dolphin
        self.user: User = user
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Device]:
        """Fetch data from Dolphin."""
        try:
            data = await self.dolphin.update(self.user)
        except Exception as err:
            raise UpdateFailed(f"Error fetching Dolphin data: {err}") from err

        if not data:
            raise UpdateFailed("No data received from the Dolphin API")

        return data
