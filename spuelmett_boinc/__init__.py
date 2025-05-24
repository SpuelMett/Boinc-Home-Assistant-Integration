"""The Boinc Control integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .boinc_control import BoincControl
from .const import BOINC_IP, CHECKPOINTING, DOMAIN, LISTENER, NAME, PASSWORD

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # create object to manage boinc
    name = entry.data.get(
        NAME, "default"
    )  # use default value, when upgrading from a version with no name in the input
    ip = entry.data[BOINC_IP]
    password = entry.data[PASSWORD]
    checkpoint_time = entry.options["checkpoint_time"]

    boinc = BoincControl(ip, password, checkpoint_time)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = boinc

    # register update options callback
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    # Register Services that can be called from automations or scripts
    async def start_boinc(call: ServiceCall) -> None:
        await boinc.start_boinc()

    async def stop_boinc(call: ServiceCall) -> None:
        await boinc.stop_boinc()

    async def soft_stop_boinc(call: ServiceCall) -> None:
        boinc.soft_stop_boinc()

    async def soft_stop_check(call: ServiceCall) -> None:
        await boinc.update()

    service_name_suffix = str(name).replace("-", "_")
    hass.services.async_register(
        DOMAIN, "start_boinc_" + service_name_suffix, start_boinc
    )
    hass.services.async_register(
        DOMAIN, "stop_boinc_" + service_name_suffix, stop_boinc
    )
    hass.services.async_register(
        DOMAIN, "soft_stop_boinc_" + service_name_suffix, soft_stop_boinc
    )
    hass.services.async_register(
        DOMAIN, "soft_stop_check_" + service_name_suffix, soft_stop_check
    )

    # Add Event listener to trigger soft stop every minute
    async def update_check(hass: HomeAssistant):
        await boinc.update()

    remove_listener = async_track_time_interval(
        hass, update_check, timedelta(minutes=1), cancel_on_shutdown=True
    )

    listener_name = LISTENER + str(name)
    hass.data[DOMAIN][listener_name] = remove_listener

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    # get name
    name = entry.data.get(
        NAME, "default"
    )  # use default value, when upgrading from a version with no name in the input

    # Remove current listener for soft stop
    listener_name = LISTENER + str(name)  # create name
    remove_listener = hass.data[DOMAIN][listener_name]
    remove_listener()

    # Unload entry
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    checkpoint_time = entry.options[CHECKPOINTING]
    hass.data[DOMAIN][entry.entry_id].set_checkpoint_time(checkpoint_time)
