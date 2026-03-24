"""Config flow for Power Dolphin integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .API.power_dolphin import PowerDolphin, User
from .const import CONF_PASSWORD, CONF_USERNAME, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Power Dolphin."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors: dict[str, str] = {}

    async def async_step_user(self, user_input: dict[str, str] | None = None) -> FlowResult:
        self._errors = {}

        if user_input is not None:
            valid = await self._test_credentials(
                user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
            )
            if valid:
                return self.async_create_entry(title="Power Dolphin", data=user_input)
            self._errors["base"] = "auth"
            return await self._show_config_form(user_input)

        return await self._show_config_form({CONF_USERNAME: "", CONF_PASSWORD: ""})

    async def _show_config_form(self, user_input: dict[str, str]) -> FlowResult:
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME,
                        default=user_input.get(CONF_USERNAME, ""),
                    ): TextSelector(
                        TextSelectorConfig(
                            type=TextSelectorType.TEXT,
                            autocomplete="username",
                        ),
                    ),
                    vol.Required(
                        CONF_PASSWORD,
                        default=user_input.get(CONF_PASSWORD, ""),
                    ): TextSelector(
                        TextSelectorConfig(
                            type=TextSelectorType.PASSWORD,
                            autocomplete="current-password",
                        ),
                    ),
                }
            ),
            errors=self._errors,
        )

    async def _test_credentials(self, username: str, password: str) -> bool:
        async with PowerDolphin() as client:
            user = User
            user.email = username
            user = await client.getAPIKey(user, password)
            if user.api != "failed":
                return True
        return False
