"""Sensors for Bracknell Bins."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .coordinator import BinDaysCoordinator

DOMAIN = "bracknell_bins"
CONF_ADDRESS_ID = "address_id"

BIN_TYPES = [
    ("Food", "Food Bin", "mdi:food-apple"),
    ("Recycling", "Recycling Bin", "mdi:recycle"),
    ("General waste", "General Waste Bin", "mdi:trash-can"),
]


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    address_id = config.get(CONF_ADDRESS_ID)
    if not address_id:
        return
    coordinator = BinDaysCoordinator(hass, address_id)
    await coordinator.async_refresh()
    async_add_entities(
        BinSensor(coordinator, round_key, friendly_name, icon)
        for round_key, friendly_name, icon in BIN_TYPES
    )


class BinSensor(CoordinatorEntity, SensorEntity):
    """A sensor representing one bin type's next collection date."""

    def __init__(self, coordinator, round_key, friendly_name, icon):
        super().__init__(coordinator)
        self._round_key = round_key
        self._attr_name = friendly_name
        self._attr_unique_id = f"bracknell_bins_{round_key.lower().replace(' ', '_')}"
        self._attr_icon = icon

    @property
    def native_value(self):
        data = self.coordinator.data
        if data and self._round_key in data:
            return data[self._round_key]["next_date"]
        return None

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if data and self._round_key in data:
            return {
                "days_until": data[self._round_key]["days_until"],
                "upcoming_collections": data[self._round_key]["upcoming"],
            }
        return {}