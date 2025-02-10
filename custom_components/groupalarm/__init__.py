"""The GroupAlarm integration."""

from __future__ import annotations

import logging
from functools import partial

from .const import DOMAIN, CONF_ORGANIZATION_ID
from .groupalarm import GroupAlarm
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_TOKEN
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

#TODO
# _PLATFORMS: list[Platform] = [Platform.BUTTON]

type GroupAlarmConfig = ConfigEntry[GroupAlarm]


# TODO Update entry annotation
async def async_setup_entry(hass: HomeAssistant, entry: GroupAlarmConfig) -> bool:
    """Set up GroupAlarm from a config entry."""

    # parameters are automatically validated in the constructor
    entry.runtime_data = ga = await hass.async_add_executor_job(
        GroupAlarm,
        entry.data[CONF_API_TOKEN],
        entry.data[CONF_ORGANIZATION_ID])

    async def async_handle_send_alarm(call: ServiceCall) -> None:
        """Handle the service call to send an alarm."""
        _LOGGER.debug("Processing alarm request: %s", call.data)

        message = call.data["message"]
        if not message:
            raise HomeAssistantError("Message parameter is required")

        # Prepare parameters
        params = {
            "message": message,
            "category": call.data.get("category"),
            "target_group": call.data.get("target_group"),
            "event_name": call.data.get("event_name"),
            "alarm_resources": call.data.get("alarm_resources"),
            "timeout": call.data.get("timeout")
        }

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        try:
            result = await hass.async_add_executor_job(partial(ga.send_groupalarm_alarm, **params))
            if not result["success"]:
                raise HomeAssistantError(
                    f"Failed to send alarm: {result.get('data', 'Unknown error')}"
                )

            _LOGGER.info("Alarm sent successfully. Response: %s", result["data"])
            hass.bus.async_fire("groupalarm_alarm_sent", {
                "alarm_id": result["data"].get("id"),
                "status": result["data"].get("status")
            })

        except Exception as err:
            _LOGGER.error("Error sending alarm: %s", err)
            raise HomeAssistantError("Failed to send alarm") from err

    # Register the service
    hass.services.async_register(
        DOMAIN,
        "send_alarm",
        async_handle_send_alarm,
        schema=vol.Schema({
            vol.Required("message"): str,
            vol.Optional("category"): str,
            vol.Optional("target_group"): str,
            vol.Optional("event_name"): str,
            vol.Optional("alarm_resources"): dict,
            vol.Optional("timeout"): int
        })
    )

    #TODO maybe create buttons and stuff
    # await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: GroupAlarmConfig) -> bool:
    """Unload a config entry."""
    # TODO
    # return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
    return True
