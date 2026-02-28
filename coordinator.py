"""Data coordinator for Bracknell Bins."""
import logging
from datetime import timedelta, datetime

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

API_URL = "https://selfservice.mybfc.bracknell-forest.gov.uk/w/webpage/waste-collection-days"
API_PARAMS = {
    "widget_action": "handle_event"
}


class BinDaysCoordinator(DataUpdateCoordinator):
    """Fetch bin collection data once per day."""

    def __init__(self, hass: HomeAssistant, address_id: str):
        super().__init__(
            hass,
            _LOGGER,
            name="Bracknell Bins",
            update_interval=timedelta(hours=12),
        )
        self._address_id = address_id

    async def _async_update_data(self):
        api_data = (
            f"code_action=find_rounds"
            f"&code_params=%7B%22addressId%22%3A%22{self._address_id}%22%7D"
            f"&action_cell_id=PCL0003988FEFFB1"
            f"&action_page_id=PAG0000570FEFFB1"
        )
        try:
            session = async_get_clientsession(self.hass)
            async with session.post(
                API_URL,
                params=API_PARAMS,
                data=api_data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "X-Requested-With": "XMLHttpRequest",
                },
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()

            if data.get("result") != "success":
                raise UpdateFailed("API returned non-success result")

            collections = {}
            today = datetime.now().date()

            for item in data["response"]["collections"]:
                round_name = item["round"]
                first_date = datetime.strptime(
                    item["firstDate"]["date"][:10], "%Y-%m-%d"
                ).date()
                days_until = (first_date - today).days

                collections[round_name] = {
                    "next_date": first_date.isoformat(),
                    "days_until": days_until,
                    "upcoming": item.get("upcomingCollections", []),
                }

            return collections

        except Exception as err:
            raise UpdateFailed(f"Error fetching bin data: {err}") from err