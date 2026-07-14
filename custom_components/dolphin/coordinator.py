import logging
from .API.dolphin import Dolphin, User, Device

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    UPDATE_INTERVAL,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class UpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Dolphin data from single endpoint."""

    def __init__(
            self, hass: HomeAssistant, dolphin: Dolphin, user: User):
        """Initialize global Dolphin data updater."""
        self.dolphin = dolphin
        self.user: User = user
        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Device]:
        """Fetch data from Dolphin."""
        try:
            result = await self.dolphin.update(self.user)
            if result is None:
                raise UpdateFailed("No data received from Dolphin API (device may be in Shabbat mode)")
            return result
        except UpdateFailed:
            raise
        except Exception as err:
            raise UpdateFailed(f"Error communicating with Dolphin API: {err}") from err