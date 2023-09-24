from time import time

class Clocker:
    MS_MAPPING = {
        "s": 1,
        "m": 60,
        "h": 60 * 60,
        "d": 24 * 60 * 60,
        "w": 7 * 24 * 60 * 60,
    }

    def __init__(self, time=time(), unit="s"):
        self.time = time
        self.unit = unit


    def add_time(self, amount: str):
        """
        Example usage: add_time("1h")
        m: minute
        w: week
        d: day
        h: hour
        s: second
        """
        if amount[-1] not in self.MS_MAPPING:
            raise ValueError("Invalid time unit")
        self.time += int(amount[:-1]) * self.MS_MAPPING[amount[-1]]
        return self

    def subtract_time(self, amount: str):
        """
        Example usage: subtract_time("1h")
        m: minute
        w: week
        d: day
        h: hour
        s: second
        """
        if amount[-1] not in self.MS_MAPPING:
            raise ValueError("Invalid time unit")
        self.time -= int(amount[:-1]) * self.MS_MAPPING[amount[-1]]
        return self
    
