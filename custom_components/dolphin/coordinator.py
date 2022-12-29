import logging
from .API.dolphin import Dolphin, User, Device

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

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
            return await self.dolphin.update(self.user)
        except:
            pass
