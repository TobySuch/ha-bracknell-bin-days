"""Sensors for Bracknell Bins."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .coordinator import BinDaysCoordinator

DOMAIN = "bracknell_bins"
CONF_ADDRESS_ID = "address_id"

BIN_TYPES = [
    # (accepted API round names, friendly name, icon). The council has renamed
    # rounds before (e.g. "Food" <-> "Food waste"), so list every known name.
    (("Food", "Food waste"), "Food Bin", "mdi:food-apple"),
    (("Recycling",), "Recycling Bin", "mdi:recycle"),
    (("General waste",), "General Waste Bin", "mdi:trash-can"),
]


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    address_id = config.get(CONF_ADDRESS_ID)
    if not address_id:
        return
    coordinator = BinDaysCoordinator(
        hass, address_id, expected_rounds=[names for names, _, _ in BIN_TYPES]
    )
    await coordinator.async_refresh()
    async_add_entities(
        BinSensor(coordinator, round_key, friendly_name, icon)
        for round_key, friendly_name, icon in BIN_TYPES
    )


class BinSensor(CoordinatorEntity, SensorEntity):
    """A sensor representing one bin type's next collection date."""

    def __init__(self, coordinator, round_names, friendly_name, icon):
        super().__init__(coordinator)
        self._round_names = round_names
        self._attr_name = friendly_name
        # Based on the first name only, so the unique ID stays stable.
        self._attr_unique_id = f"bracknell_bins_{round_names[0].lower().replace(' ', '_')}"
        self._attr_icon = icon

    def _round_data(self):
        data = self.coordinator.data or {}
        for name in self._round_names:
            if name in data:
                return data[name]
        return None

    @property
    def native_value(self):
        item = self._round_data()
        return item["next_date"] if item else None

    @property
    def extra_state_attributes(self):
        item = self._round_data()
        if item:
            return {
                "days_until": item["days_until"],
                "upcoming_collections": item["upcoming"],
            }
        return {}