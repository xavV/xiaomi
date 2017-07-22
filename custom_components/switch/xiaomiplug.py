"""
Support for Xiaomi Smart WiFi Socket and Smart Power Strip.

For more details about this platform, please refer to the documentation
https://home-assistant.io/components/switch.xiaomi_plug/
"""
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.switch import SwitchDevice, PLATFORM_SCHEMA
from homeassistant.const import (DEVICE_DEFAULT_NAME,
                                 CONF_NAME, CONF_HOST, CONF_TOKEN)

_LOGGER = logging.getLogger(__name__)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_TOKEN): vol.All(str, vol.Length(min=32, max=32)),
    vol.Optional(CONF_NAME): cv.string,
})

REQUIREMENTS = ['python-mirobo==0.1.2']

ATTR_POWER = 'power'
ATTR_TEMPERATURE = 'temperature'
ATTR_CURRENT = 'current'


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices_callback, discovery_info=None):
    """Set up the plug from config."""
    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)
    token = config.get(CONF_TOKEN)

    add_devices_callback([XiaomiPlugSwitch(name, host, token)], True)


class XiaomiPlugSwitch(SwitchDevice):
    """Representation of a Xiaomi Plug."""

    def __init__(self, name, host, token):
        """Initialize the plug switch."""
        self._name = name or DEVICE_DEFAULT_NAME
        self._icon = 'mdi:power-socket'
        self.host = host
        self.token = token

        self._plug = None
        self._state = None
        self._state_attrs = {
            ATTR_TEMPERATURE: None,
            ATTR_CURRENT: None
        }


    @property
    def should_poll(self):
        """Poll the plug."""
        return True

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def icon(self):
        """Return the icon to use for device if any."""
        return self._icon

    @property
    def available(self):
        """Return true when state is known."""
        return self._state is not None

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        return self._state_attrs

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._state

    @property
    def plug(self):
        """Property accessor for plug object."""
        if not self._plug:
            from mirobo import Plug
            _LOGGER.info("initializing with host %s token %s",
                         self.host, self.token)
            self._plug = Plug(self.host, self.token)

        return self._plug

    def turn_on(self, **kwargs):
        """Turn the plug on."""
        self.plug.on()
        self._state = True

    def turn_off(self, **kwargs):
        """Turn the plug off."""
        self.plug.off()
        self._state = False

    def update(self):
        """Fetch state from the device."""
        from mirobo import DeviceException
        try:
            state = self.plug.status()
            _LOGGER.debug("got state from the plug: %s", state)

            self._state_attrs = {
                ATTR_TEMPERATURE: state.temperature,
                ATTR_CURRENT: state.current,
            }

            self._state = state.is_on
        except DeviceException as ex:
            _LOGGER.error("Got exception while fetching the state: %s", ex)
