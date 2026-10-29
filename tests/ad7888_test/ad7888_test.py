from app.ad7888_driver import *
from time import sleep

def main():
    ad7888 = AD7888(0, 0)
    while True:
        print("AD7888: " + ad7888.read_data() + "\n")
        sleep(1)

if __name__ == "__main__":
    main()