from .device import Device, DeviceException


class Plug(Device):
    """Main class representing the smart wifi socket / plug."""

    def __init__(self, ip: str, token: str, start_id: int = 0, debug: int = 0) -> None:
        super().__init__(ip, token, start_id, debug)
        self.manual_seqnum = -1

    def start(self):
        """Start cleaning."""
        return self.send("set_power", ["on"])

    def stop(self):
        """Stop cleaning."""
        return self.send("set_power", ["off"])

    def status(self):
        return self.send("get_prop", ["power"])[0]

    def raw_command(self, cmd, params):
        """Send a raw command to the robot."""
        return self.send(cmd, params)
