from ad7888_driver import AD7888
from ad7888_driver import AIN1

class ADC:
    def __init__(self, channel=AIN1):
        self.adc = AD7888(0, 0)
        self._VREF = 3.3
        self._MAX_RAW_VALUE = 4095

    def read_voltage(self):
        raw_data = self.adc.read_data()
        return ((self._VREF * raw_data) / self._MAX_RAW_VALUE)

    def voltTopercentage(self, volt):
        return (volt / self._VREF)

    

