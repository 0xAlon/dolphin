class Device(object):
    device_name: str
    nickname: str

    def __init__(self, device_name: str = None, nickname: str = None):
        self.device_name = device_name if device_name else None
        self.nickname = nickname if not "None" else None


class Data(object):
    power: str
    temperature: str
    target: str

    def __init__(self, power: str = None, temperature: str = None, target: str = None):
        self.power = power if power else None
        self.temperature = temperature if temperature else None
        self.target = target if target else None


class Energy(object):
    energy: str

    def __init__(self, energy: str = None):
        self.energy = energy if energy else None


class Settings(object):
    shabbat: str
    isFixedTemperatureEnabled: str

    def __init__(self, shabbat: str = None, fixed_temperature: str = None):
        self.shabbat = shabbat if shabbat else None
        self.fixed_temperature = fixed_temperature if fixed_temperature else None
