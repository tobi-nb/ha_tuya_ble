"""Config flow for Tuya BLE integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_ADDRESS, CONF_DEVICE_ID
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_CATEGORY,
    CONF_DEVICE_NAME,
    CONF_LOCAL_KEY,
    CONF_PRODUCT_ID,
    CONF_PRODUCT_MODEL,
    CONF_PRODUCT_NAME,
    CONF_UUID,
    DOMAIN,
)
from .devices import get_device_readable_name
from .tuya_ble import SERVICE_UUID


class TuyaBLEConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tuya BLE."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        super().__init__()
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered_devices: dict[str, BluetoothServiceInfoBleak] = {}

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> FlowResult:
        """Handle the bluetooth discovery step."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self._discovery_info = discovery_info
        self.context["title_placeholders"] = {
            "name": await get_device_readable_name(discovery_info, None)
        }
        return await self.async_step_credentials()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the user step."""
        if discovery := self._discovery_info:
            self._discovered_devices[discovery.address] = discovery
        else:
            current_addresses = self._async_current_ids()
            for discovery in async_discovered_service_info(self.hass):
                if (
                    discovery.address in current_addresses
                    or discovery.address in self._discovered_devices
                    or discovery.service_data is None
                    or SERVICE_UUID not in discovery.service_data.keys()
                ):
                    continue
                self._discovered_devices[discovery.address] = discovery

        if not self._discovered_devices:
            return self.async_abort(reason="no_unconfigured_devices")

        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            self._discovery_info = self._discovered_devices[address]
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            return await self.async_step_credentials()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ADDRESS): vol.In(
                        {
                            service_info.address: await get_device_readable_name(
                                service_info, None
                            )
                            for service_info in self._discovered_devices.values()
                        }
                    ),
                },
            ),
        )

    async def async_step_credentials(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual entry of the device's local credentials."""
        errors: dict[str, str] = {}

        if user_input is not None:
            discovery_info = self._discovery_info
            return self.async_create_entry(
                title=await get_device_readable_name(discovery_info, None),
                data={CONF_ADDRESS: discovery_info.address},
                options={
                    CONF_ADDRESS: discovery_info.address,
                    CONF_DEVICE_ID: user_input[CONF_DEVICE_ID],
                    CONF_LOCAL_KEY: user_input[CONF_LOCAL_KEY],
                    CONF_UUID: user_input[CONF_DEVICE_ID],
                    CONF_CATEGORY: user_input[CONF_CATEGORY],
                    CONF_PRODUCT_ID: user_input.get(CONF_PRODUCT_ID, ""),
                    CONF_DEVICE_NAME: user_input.get(CONF_DEVICE_NAME, ""),
                    CONF_PRODUCT_MODEL: user_input.get(CONF_DEVICE_NAME, ""),
                    CONF_PRODUCT_NAME: user_input.get(CONF_DEVICE_NAME, ""),
                },
            )

        return self.async_show_form(
            step_id="credentials",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DEVICE_ID): str,
                    vol.Required(CONF_LOCAL_KEY): str,
                    vol.Required(CONF_CATEGORY): str,
                    vol.Optional(CONF_PRODUCT_ID): str,
                    vol.Optional(CONF_DEVICE_NAME): str,
                }
            ),
            errors=errors,
        )
