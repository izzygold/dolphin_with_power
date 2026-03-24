import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .API.models import Device, User
from .API.power_dolphin import PowerDolphin
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER: logging.Logger = logging.getLogger(__package__)


class UpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Dolphin boiler data from the cloud API."""

    def __init__(
        self, hass: HomeAssistant, power_dolphin: PowerDolphin, user: User
    ) -> None:
        """Initialize global Power Dolphin data updater."""
        self.power_dolphin = power_dolphin
        self.user: User = user
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Device]:
        """Fetch data from Dolphin cloud."""
        try:
            return await self.power_dolphin.update(self.user)
        except:
            pass
