from app.adc_driver import *
from time import sleep

def main():
    adc = ADC()
    while True:
        volt = adc.read_voltage()
        percentage = adc.voltTopercentage(volt)
        print(f"ADC: voltaje {volt} | porcentaje {percentage} \n")
        sleep(1)

if __name__ == "__main__":
    main()

    