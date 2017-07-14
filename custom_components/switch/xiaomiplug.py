
from homeassistant.components.switch import SwitchDevice
from homeassistant.const import DEVICE_DEFAULT_NAME, CONF_NAME, CONF_HOST
import logging

_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['construct==2.8.12', 'cryptography==1.9', 'click==6.7']

def setup_platform(hass, config, add_devices_callback, discovery_info=None):
    import xiaomiplug

    """Setup the xiaomi smart wifi socket."""
    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)
    token = config.get('token')

    add_devices_callback([
        XiaomiSwitch(name, host, token)
    ])


class XiaomiSwitch(SwitchDevice):
    """Representation of a xiaomi switch."""

    def __init__(self, name, host, token):
        """Initialize the switch."""
        self._name = name or DEVICE_DEFAULT_NAME
        self.host = host
        self.token = token
        self._switch = None
        self._state = None

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
        return 'mdi:broom'

    @property
    def available(self):
        return self._state is not None

    @property
    def is_on(self):
        """Return true if plug is on."""
        return self._state

    @property
    def switch(self):
        if not self._switch: 
           from xiaomiplug import Plug
           _LOGGER.info("initializing with host %s token %s" % (self.host, self.token))
           self._switch = Plug(self.host, self.token)

        return self._switch

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self.switch.start()
        self._state = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self.switch.stop()
        self._state = False
        self.schedule_update_ha_state()

    def update(self):
        try:
            state = self.switch.status()
            _LOGGER.info("got status: %s" % state)

            if state == "on":
                self._state = True
            else:
                self._state = False

        except Exception as ex:
            _LOGGER.error("Got exception while fetching the state: %s" % ex)

