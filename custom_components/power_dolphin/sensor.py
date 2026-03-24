import logging
from contextlib import suppress
from datetime import datetime, timezone
from typing import Callable, List

import homeassistant.core
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    UnitOfElectricCurrent,
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo, Entity, async_generate_entity_id
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NOMINAL_VOLTAGE_V
from .coordinator import UpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1


def _current_amperes(device) -> float:
    try:
        return float(device.energy)
    except (TypeError, ValueError):
        return 0.0


async def async_setup_entry(
    hass: homeassistant.core.HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[List[Entity], bool], None],
) -> None:
    coordinator: UpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[Entity] = []

    for device in coordinator.data.keys():
        if await coordinator.power_dolphin.isEnergyMeter(
            coordinator.power_dolphin._user, device
        ) == "1":
            entities.append(
                PowerDolphinElectricCurrentSensor(hass=hass, coordinator=coordinator, device=device)
            )
            entities.append(
                PowerDolphinCalculatedPowerSensor(hass=hass, coordinator=coordinator, device=device)
            )
            entities.append(
                PowerDolphinCalculatedEnergySensor(hass=hass, coordinator=coordinator, device=device)
            )

    async_add_entities(entities)


class PowerDolphinElectricCurrentSensor(CoordinatorEntity, SensorEntity):
    """Reported electric current from the boiler API (device.energy field)."""

    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_icon = "mdi:current-ac"

    def __init__(self, hass, coordinator, device):
        super().__init__(coordinator)
        self._hass = hass
        self._device = device
        self.entity_id = async_generate_entity_id(
            DOMAIN + ".{}",
            f"{device}_electric_current",
            hass=hass,
        )

    @property
    def unique_id(self):
        return self.entity_id

    @property
    def name(self):
        return "Electric current"

    @property
    def native_value(self):
        return _current_amperes(self.coordinator.data[self._device])

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._device)},
            name=self.name,
        )


class PowerDolphinCalculatedPowerSensor(CoordinatorEntity, SensorEntity):
    """Apparent power from P = nominal_voltage × I (assumes unity PF)."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_icon = "mdi:flash"
    _attr_suggested_display_precision = 0

    def __init__(self, hass, coordinator, device):
        super().__init__(coordinator)
        self._hass = hass
        self._device = device
        self.entity_id = async_generate_entity_id(
            DOMAIN + ".{}",
            f"{device}_electric_power",
            hass=hass,
        )

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self._device}_electric_power"

    @property
    def name(self):
        return "Electric power"

    @property
    def native_value(self):
        return round(NOMINAL_VOLTAGE_V * _current_amperes(self.coordinator.data[self._device]), 3)

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(identifiers={(DOMAIN, self._device)})


class PowerDolphinCalculatedEnergySensor(CoordinatorEntity, SensorEntity, RestoreEntity):
    """Energy (kWh) by integrating calculated power over time between coordinator updates."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_icon = "mdi:lightning-bolt-circle"
    _attr_suggested_display_precision = 3

    def __init__(self, hass, coordinator, device):
        super().__init__(coordinator)
        self._hass = hass
        self._device = device
        self._energy_kwh = 0.0
        self._last_ts: datetime | None = None
        self._last_amps: float | None = None
        self.entity_id = async_generate_entity_id(
            DOMAIN + ".{}",
            f"{device}_electric_energy",
            hass=hass,
        )

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self._device}_electric_energy"

    @property
    def name(self):
        return "Electric energy"

    @property
    def native_value(self):
        return round(self._energy_kwh, 6)

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(identifiers={(DOMAIN, self._device)})

    async def async_added_to_hass(self) -> None:
        await RestoreEntity.async_added_to_hass(self)
        await CoordinatorEntity.async_added_to_hass(self)
        if (last_state := await self.async_get_last_state()) is not None:
            with suppress(ValueError, TypeError):
                if last_state.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE, None, ""):
                    self._energy_kwh = float(last_state.state)

    @callback
    def _handle_coordinator_update(self) -> None:
        self._accumulate_energy_since_last_sample()
        super()._handle_coordinator_update()

    def _accumulate_energy_since_last_sample(self) -> None:
        now = datetime.now(timezone.utc)
        current_a = _current_amperes(self.coordinator.data[self._device])
        if self._last_ts is not None and self._last_amps is not None:
            dt_h = (now - self._last_ts).total_seconds() / 3600.0
            if dt_h > 0:
                avg_w = NOMINAL_VOLTAGE_V * (self._last_amps + current_a) / 2.0
                self._energy_kwh += (avg_w / 1000.0) * dt_h
        self._last_ts = now
        self._last_amps = current_a
