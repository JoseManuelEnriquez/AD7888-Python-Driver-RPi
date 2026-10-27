import threading
from gpiozero import LED

LED_GPIO = 17

def led_init():
    return LED(LED_GPIO)

class LED_thread(threading.Thread):
    def __init__(self, led):
        super().__init__()
        self.led = led
        self._stop_led = threading.Event()
        self.period_s = 0.5

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            self.led.toggle()
            self._stop_event.wait(self.period_s)


