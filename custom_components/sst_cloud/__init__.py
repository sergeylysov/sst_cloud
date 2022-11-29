from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import asyncio
from . import sst
from .const import DOMAIN
import logging
_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[str] = ["climate","sensor", "binary_sensor", "switch","number"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    #Создать объект с подключением к сервису
    sst1 = sst.SST(hass, entry.data["username"], entry.data["password"])
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = sst1
    await hass.async_add_executor_job(
             sst1.pull_data
         )

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
