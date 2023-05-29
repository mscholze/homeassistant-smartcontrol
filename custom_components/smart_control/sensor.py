"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    STATE_CLASS_TOTAL_INCREASING,
    DEVICE_CLASS_ENERGY,
)
from homeassistant.const import ENERGY_KILO_WATT_HOUR, POWER_WATT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from .smart_control_api import get_token, get_watts, get_kWh, write_to_file

import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    username = config.get("username")
    password = config.get("password")

    add_entities([
        SmartControlEnergyConsumptionTotalSensor(username, password),
        SmartControlPowerConsumptionSensor(username, password)
    ])


class SmartControlEnergyConsumptionTotalSensor(SensorEntity):
    """Representation of a Smart Control Energy Consumption Total Sensor."""

    _attr_name = "Smart Control Energy Consumption Total"
    _attr_unit_of_measurement = ENERGY_KILO_WATT_HOUR
    _attr_device_class = DEVICE_CLASS_ENERGY
    _attr_state_class = STATE_CLASS_TOTAL_INCREASING

    def __init__(self, username: str, password: str) -> None:
        self._username = username
        self._password = password
        self._access_token = None

    async def async_update(self):
        """Fetch new state data for the sensor."""
        try:
            if self._access_token is None:
                self._access_token = await get_token(self._username, self._password)
                write2file(self._access_token)

            loop = asyncio.get_event_loop()
            await loop.create_task(self.fetch_kWh())
        except asyncio.CancelledError:
            pass
        except Exception as e:
            _LOGGER.error("Error updating sensor: %s", e)

    async def fetch_kWh(self):
        """Fetch the kWh value."""
        try:
            kWh = await get_kWh(self._access_token)
            self._attr_native_value = kWh
        except asyncio.CancelledError:
            pass
        except Exception as e:
            _LOGGER.error("Error fetching kWh: %s", e)


class SmartControlPowerConsumptionSensor(SensorEntity):
    """Representation of a Smart Control Power Consumption Sensor."""
    _attr_name = "Smart Control Power Consumption"
    _attr_unit_of_measurement = POWER_WATT

    def __init__(self, username: str, password: str) -> None:
        self._username = username
        self._password = password
        self._access_token = None

    async def async_update(self):
        """Fetch new state data for the sensor."""
        try:
            if self._access_token is None:
                self._access_token = await get_token(self._username, self._password)
                write2file(self._access_token)

            loop = asyncio.get_event_loop()
            await loop.create_task(self.fetch_watts())
        except asyncio.CancelledError:
            pass
        except Exception as e:
            _LOGGER.error("Error updating sensor: %s", e)

    async def fetch_watts(self):
        """Fetch the watts value."""
        try:
            watts = await get_watts(self._access_token)
            self._attr_native_value = watts
        except asyncio.CancelledError:
            pass
        except Exception as e:
            _LOGGER.error("Error fetching watts: %s", e)
