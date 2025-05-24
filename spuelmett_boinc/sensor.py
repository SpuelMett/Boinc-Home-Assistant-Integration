from dataclasses import dataclass
import logging

from config.custom_components.spuelmett_boinc.const import (
    AVERAGE_PROGRESS_RATE,
    RUNNING_TASK_COUNT,
    TOTAL_TASK_COUNT,
)
from config.custom_components.spuelmett_boinc.coordinator import BoincCoordinator
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.components.sensor.const import SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

_LOGGER = logging.getLogger(__name__)


@dataclass
class RunningTaskEntityDescription(SensorEntityDescription):
    """Provide a description of the sensor."""

    # For backwards compat, allow description to override unique ID key to use
    unique_id: str | None = None


SENSORS = (
    RunningTaskEntityDescription(
        key=RUNNING_TASK_COUNT,
        translation_key="task_running",
        unique_id="taskrunning",
        # No unit, it's extracted from response.
    ),
    RunningTaskEntityDescription(
        key=TOTAL_TASK_COUNT,
        translation_key="task_total",
        unique_id="tasktotal",
        # No unit, it's extracted from response.
    ),
    RunningTaskEntityDescription(
        key=AVERAGE_PROGRESS_RATE,
        translation_key="average_progress_rate",
        unique_id="average_progress_rate",
        # No unit, it's extracted from response.
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensor."""
    coordinator = entry.runtime_data

    async_add_entities(
        [BoincSensor(coordinator, description) for description in SENSORS], False
    )


class BoincSensor(CoordinatorEntity[BoincCoordinator], SensorEntity):
    """Implementation of the sensor."""

    entity_description: RunningTaskEntityDescription
    _attr_has_entity_name = True
    _attr_icon = "mdi:numeric"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = None
    _attr_device_class = None

    def __init__(
        self, coordinator: BoincCoordinator, description: RunningTaskEntityDescription
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.get_entry_name()}_{description.key}"

    @property
    def available(self) -> bool:
        return True

    @property
    def native_value(self) -> int | None:
        """Return sensor state."""
        if (value := self.coordinator.data[self.entity_description.key]) is None:
            return None
        return value

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
