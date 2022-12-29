from typing import Any
import logging

_LOGGER = logging.getLogger(__name__)


class User:
    """Object holding all information of Dolphin user."""

    api: str = None
    email: str = None
    device: list[dict[str: str], dict[str:str]] = None

    def __init__(self, data: dict[str, Any] | str) -> None:
        self.update_from_dict(data)

    def update_from_dict(self, data: dict[str, Any] | str):
        if _api := data:
            if type(_api) == str:
                self.api = _api
            else:
                self.device = _api


class Device:
    """Object holding all information of Dolphin device."""

    power: bool = False
    energy: float = 0
    temperature: float = None
    targetTemperature: int = None
    showerTemperature: dict[int: int] = None
    shabbat: bool = False
    fixedTemperature: bool = False

    def __init__(self, data: dict[str, Any]) -> None:
        self.update_from_dict(data)

    def update_from_dict(self, data: dict[str, Any]):
        """Return Device object from Dolphin API response."""

        if _power := data.get("Power"):
            self.power = True if _power == "ON" else False

        if _energy := data.get("Energy"):
            self.energy = _energy
        else:
            self.energy = 0

        if _temperature := data.get("Temperature"):
            self.temperature = _temperature if _temperature > 0 else None

        if _targetTemperature := data.get("targetTemperature"):
            self.targetTemperature = _targetTemperature if _targetTemperature > 0 else 20

        if _showerTemperature := data.get("showerTemperature"):
            self.showerTemperature = _showerTemperature

        if _shabbat := data.get("Shabbat"):
            self.shabbat = True if _shabbat == "ON" else False

        if _fixedTemperature := data.get("fixedTemperature"):
            self.fixedTemperature = True if _fixedTemperature == "ON" else False
        # else:
        #    self.fixedTemperature = False

        return self
