from datetime import timedelta
import logging

from config.custom_components.spuelmett_boinc.const import (
    AVERAGE_PROGRESS_RATE,
    NAME,
    RUNNING_TASK_COUNT,
    TOTAL_TASK_COUNT,
)
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class BoincCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry,
        boinc,
    ):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Boinc sensor",
            config_entry=config_entry,
            update_interval=timedelta(seconds=30),
            always_update=True,
        )
        self._device: SensorDeviceClass | None = None
        self.boinc = boinc

    @property
    def entry_id(self) -> str:
        return self.config_entry.entry_id

    def get_entry_name(self) -> str:
        return self.config_entry.data.get(NAME, "default")

    async def _async_update_data(self):
        data = {}
        data[RUNNING_TASK_COUNT] = await self.boinc.get_running_task_count()
        data[TOTAL_TASK_COUNT] = await self.boinc.get_total_task_count()
        data[AVERAGE_PROGRESS_RATE] = await self.boinc.average_progress_rate()

        return data
