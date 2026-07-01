"""The Tuya BLE integration."""
from __future__ import annotations

import logging

from typing import Any

from homeassistant.const import CONF_DEVICE_ID
from homeassistant.core import HomeAssistant

from .tuya_ble import (
    AbstaractTuyaBLEDeviceManager,
    TuyaBLEDeviceCredentials,
)

from .const import (
    CONF_PRODUCT_MODEL,
    CONF_UUID,
    CONF_LOCAL_KEY,
    CONF_CATEGORY,
    CONF_PRODUCT_ID,
    CONF_DEVICE_NAME,
    CONF_PRODUCT_NAME,
    CONF_FUNCTIONS,
    CONF_STATUS_RANGE,
)

_LOGGER = logging.getLogger(__name__)


class LocalTuyaBLEDeviceManager(AbstaractTuyaBLEDeviceManager):
    """Manager of the Tuya BLE devices credentials, sourced from local config entry data only."""

    def __init__(self, hass: HomeAssistant, data: dict[str, Any]) -> None:
        assert hass is not None
        self._hass = hass
        self._data = data

    async def get_device_credentials(
        self,
        address: str,
        force_update: bool = False,
        save_data: bool = False,
    ) -> TuyaBLEDeviceCredentials | None:
        """Get credentials of the Tuya BLE device from locally stored config data."""
        return self.check_and_create_device_credentials(
            self._data.get(CONF_UUID),
            self._data.get(CONF_LOCAL_KEY),
            self._data.get(CONF_DEVICE_ID),
            self._data.get(CONF_CATEGORY),
            self._data.get(CONF_PRODUCT_ID),
            self._data.get(CONF_DEVICE_NAME),
            self._data.get(CONF_PRODUCT_MODEL),
            self._data.get(CONF_PRODUCT_NAME),
            self._data.get(CONF_FUNCTIONS, []),
            self._data.get(CONF_STATUS_RANGE, []),
        )

    @property
    def data(self) -> dict[str, Any]:
        return self._data
