"""Contains binary sensor entities for SpuelMett Boinc integration."""

from dataclasses import dataclass
import logging

from config.custom_components.spuelmett_boinc.coordinator import BoincCoordinator
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import AVAILABLE

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=False)
class BoincBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes Boinc binary sensor entity."""

    # For backwards compat, allow description to override unique ID key to use
    unique_id: str | None = None


BINARY_SENSORS = (
    BoincBinarySensorEntityDescription(
        key=AVAILABLE,
        translation_key="available",
        unique_id="available",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,  # AddConfigEntryEntitiesCallback, AddEntitiesCallback
) -> None:
    """Set up sensor platform."""
    coordinator = config_entry.runtime_data

    async_add_entities(
        [
            BoincSensorEntity(config_entry, description, coordinator)
            for description in BINARY_SENSORS
        ],
        False,
    )


class BoincSensorEntity(CoordinatorEntity[BoincCoordinator], BinarySensorEntity):
    """Represents a binary sensor entity for Hoymiles WiFi integration."""

    entity_description: BoincBinarySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        config_entry: ConfigEntry,
        description: BoincBinarySensorEntityDescription,
        coordinator: BoincCoordinator,
    ):
        """Initialize the HoymilesInverterSensorEntity."""
        super().__init__(coordinator)
        self._native_value = None
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.get_entry_name()}_{description.key}"

    @property
    def is_on(self):
        """Return the state of the binary sensor."""
        return self.native_value

    @property
    def available(self) -> bool:
        return True

    @property
    def native_value(self) -> bool | None:
        """Return sensor state."""
        if (value := self.coordinator.data[self.entity_description.key]) is None:
            return None
        return value

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
