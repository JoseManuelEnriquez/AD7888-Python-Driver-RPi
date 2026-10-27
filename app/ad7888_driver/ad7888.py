import spidev 
from parameters import *

FREQUENCY = 500_000 

class AD7888:   

    def __init__(self, spi_bus, device_cs, channel=AIN1, ref=0, mode=NORMAL_MODE):
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, device_cs)
        self.spi.max_speed_hz = FREQUENCY
        self.spi.mode = 0b11
        self.spi.bits_per_word = 8

        self.set_channel(channel)
        self.set_reference(ref)
        self.set_power_mode(mode)

    def set_channel(self, channel):
        self.channel = channel

    def set_reference(self, reference):
        self.ref= reference

    def set_power_mode(self, mode):
        handlers = {
            NORMAL_MODE: self._send_normal_mode,
            SHUTDOWN_MODE: self._send_shutdown_mode,
            AUTO_SHUTDOWN_MODE: self._send_auto_shutdown_mode,
            STANDBY_MODE: self._send_standby_mode,
        }
        if mode not in handlers:
            raise ValueError(f"Modo de energía no válido: {mode}")
        self.mode = mode              # bits PM1/PM0
        self.read_cb = handlers[mode]

    
    def _send_shutdown_mode(self):
        raise NotImplementedError

    def _send_auto_shutdown_mode(self):
        raise NotImplementedError

    def _send_standby_mode(self):
        raise NotImplementedError
        
    
    def _send_normal_mode(self):
        '''
        El spi esta configurado 8 bits per word, entonces el spi genera siempre 8 ciclos de reloj. 

        Segun el datasheet, el ADC en modo normal necesita 16 ciclos de SCLK para poder ver el resultado de la conversion.
        Por eso se envia dos bytes, el primer byte genera los 8 primeros ciclos para configurar el control register.
        Y el siguiente para generar otros 8 ciclos, y poder leer el resultado de la conversion.
 
        ANOTACION: Se debe mantener los bits de PM1 y PM0 para que funcione
        '''
        # 16 ciclos de SCLK en una sola trama (CS bajo durante los 2 bytes).
        ctrl = (self.channel << 3) | (self.ref << 2) | self.mode
        rx = self.spi.xfer2([ctrl, ctrl])
        # Trama de salida: 4 ceros + 12 bits de datos
        return ((rx[0] & 0x0F) << 8) | rx[1]

    def read_data(self):
        return self.read_cb()

    def close(self):
        self.spi.close()

