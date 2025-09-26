"""Platform for sensor integration."""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfEnergy, UnitOfPower
from homeassistant.helpers.entity import DeviceInfo

from .smart_control_api import get_token, get_watts, get_kWh, write_to_file

import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

def write2file(*_args, **_kwargs):
    """Disabled debug file writer – does nothing."""
    return

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
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

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
    _attr_native_unit_of_measurement = UnitOfPower.WATT

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