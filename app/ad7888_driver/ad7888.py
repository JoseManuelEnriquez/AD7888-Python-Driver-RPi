import spidev 
import NORMAL_MODE, SHUTDOWN_MODE, AUTO_SHUTDOWN_MODE, STANDBY_MODE from parameters

FREQUENCY = 500000
PERIOD_US = 1.0 / FREQUENCY  
BYTE_PER_WORD = 16

class AD7888:

    def __init__(self, spi_bus, device_cs):
        self.spi = spidev.Spidev()
        self.spi.open(spi_bus, device_cs)
        self.spi.max_speed_hz(FREQUENCY)
        self.spi.mode = 0
        self.spi.bits_per_word = 8

    def set_channel(self, channel):
        self.channel = channel

    def set_reference(self, reference):
        self.ref= reference

    def set_power_mode(self, mode):
        if(mode == NORMAL_MODE):
            self.read_cb = self._send_normal_mode
        elif(mode == SHUTDOWN_MODE):
            self.read_cb = self._send_shutdown_mode
        elif(mode == AUTO_SHUTDOWN_MODE):
            self.read_cb = self._send_auto_shutdown_mode
        elif(mode == STANDBY_MODE):
            self.read_cb = self._send_standby_mode
            
    def _send_shutdown_mode(self):
        pass

    def _send_auto_shutdown_mode(self):
        pass

    def _send_standby_mode(self):
        pass
    
    def _send_normal_mode(self):
        '''
        El spi esta configurado 8 bits per word, entonces el spi genera siempre 8 ciclos de reloj. 

        Segun el datasheet, el ADC en modo normal necesita 16 ciclos de SCLK para poder ver el resultado de la conversion.
        Por eso se envia dos bytes, el primer byte genera los 8 primeros ciclos para configurar el control register.
        Y el siguiente para generar otros 8 ciclos, y poder leer el resultado de la conversion.
 
        ANOTACION: Se debe mantener los bits de PM1 y PM0 para que funcione
        '''
        data_byte = [(0x00 | (self.channel << 3) | (self.ref << 2) | (self.mode)), (0x00 | (self.mode))]
        data_rx = self.spi.xfer2(data_byte)
        return (data_rx >> 4) # Se desplaza 4 posiciones porque el ADC agrega 4 ceros primero

    def read_data(self):
        self.read_cb()

