from time import sleep
from led import LED_thread, led_init
from adc_driver import ADC
from collections import deque
from time import sleep

MAX_READ_ADC = 11

def read_adc(adc):
    volt = 0.0
    for i in range (0, MAX_READ_ADC):
        volt =  volt + adc.read_voltage()
    
    return (volt / MAX_READ_ADC)

def feed(buf, volt):
    buf.append(volt)

def update_voltages(adc, buf):
    volt = read_adc(adc)
    feed(buf, volt)

def calculate_percetange(adc, buf):
    volt = (sum(buf) / len(buf))
    return adc.voltTopercentage(volt)

blink = False

def led_blinking(percentage, led_thread):
    if percentage <= 0.33:
        led_thread.start()
        blink = True
    else:
        if blink:
            blink = False
            led_thread.stop()
            led_thread.join()

def init_buf(adc, buf):
    for i in range(0, 5):
        update_voltages(adc,buf)

def main():
    led_thread = LED_thread(led_init())
    adc = ADC()
    buf = deque(maxlen=5)
    init_buf(adc, buf)
    
    while True:
        update_voltages(adc, buf)
        percentage = calculate_percetange(adc, buf)
        led_blinking(percentage, led_thread)
        sleep(10)

if __name__ == "__main__":
    main()
    
