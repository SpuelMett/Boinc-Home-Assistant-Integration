"""Config flow for Boinc Control integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import OptionsFlow
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, BOINC_IP, PASSWORD, CHECKPOINTING
from .pyboinc.pyboinc import init_rpc_client

_LOGGER = logging.getLogger(__name__)


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(BOINC_IP): str,
        vol.Required(PASSWORD): str,
        vol.Required(CHECKPOINTING, default=120): vol.All(
            vol.Coerce(int), vol.Range(min=61, max=360)
        ),
    }
)

STEP_CONFIGURE = vol.Schema(
    {
        vol.Required(CHECKPOINTING, default=120): vol.All(
            vol.Coerce(int), vol.Range(min=61, max=3600)
        ),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    ip = data[BOINC_IP]
    password = data[PASSWORD]

    authorize_answer = False
    try:
        rpc_client = await init_rpc_client(ip, password)
        authorize_answer = await rpc_client.authorize()
    except:
        raise CannotConnect

    if authorize_answer is True:
        return {"title": "Boinc control"}
    else:
        raise InvalidAuth


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Boinc Control."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=info["title"],
                    data={
                        BOINC_IP: user_input[BOINC_IP],
                        PASSWORD: user_input[PASSWORD],
                    },
                    options={CHECKPOINTING: user_input[CHECKPOINTING]},
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class OptionsFlowHandler(OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "checkpoint_time",
                        default=self.config_entry.options.get("checkpoint_time"),
                    ): int
                }
            ),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
