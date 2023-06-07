"""The Boinc Control integration."""
from __future__ import annotations
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.core import ServiceCall, callback

from .const import DOMAIN, LISTENER, CHECKPOINTING
from .boinc_control import BoincControl


PLATFORMS: list[Platform] = []  # [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # create object to manage boinc
    ip = entry.data["remote_ip"]
    password = entry.data["password"]
    checkpoint_time = entry.options["checkpoint_time"]

    boinc = BoincControl(ip, password, checkpoint_time)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = boinc

    # register update options callback
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    # Register Services that can be called from automations or scripts
    @callback
    async def start_boinc(call: ServiceCall) -> None:
        await boinc.start_boinc()

    @callback
    async def stop_boinc(call: ServiceCall) -> None:
        await boinc.stop_boinc()

    @callback
    async def soft_stop_boinc(call: ServiceCall) -> None:
        boinc.soft_stop_boinc()

    @callback
    async def soft_stop_check(call: ServiceCall) -> None:
        await boinc.update()

    hass.services.async_register(DOMAIN, "start_boinc", start_boinc)
    hass.services.async_register(DOMAIN, "stop_boinc", stop_boinc)
    hass.services.async_register(DOMAIN, "soft_stop_boinc", soft_stop_boinc)
    hass.services.async_register(DOMAIN, "soft_stop_check", soft_stop_check)

    # Add Event listener to trigger soft stop every minute
    async def update_check(hass: HomeAssistant):
        await boinc.update()

    remove_listener = hass.helpers.event.async_track_time_interval(
        update_check, timedelta(minutes=1), cancel_on_shutdown=True
    )
    hass.data[DOMAIN][LISTENER] = remove_listener

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    # Remove current listener for soft stop
    remove_listener = hass.data[DOMAIN][LISTENER]
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
