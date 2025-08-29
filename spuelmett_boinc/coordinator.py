from datetime import timedelta
import logging

from .const import (
    AVERAGE_PROGRESS_RATE,
    NAME,
    RUNNING_TASK_COUNT,
    TOTAL_TASK_COUNT,
    AVAILABLE,
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
            update_interval=timedelta(seconds=60),
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
        results = await self.boinc.get_results()
        data = {}

        if results is not None:
            data[RUNNING_TASK_COUNT] = self.boinc.get_running_task_count(results)
            data[TOTAL_TASK_COUNT] = self.boinc.get_total_task_count(results)
            data[AVERAGE_PROGRESS_RATE] = self.boinc.average_progress_rate(results)
        else:
            data[RUNNING_TASK_COUNT] = None
            data[TOTAL_TASK_COUNT] = None
            data[AVERAGE_PROGRESS_RATE] = None

        data[AVAILABLE] = await self.boinc.get_available()

        return data
