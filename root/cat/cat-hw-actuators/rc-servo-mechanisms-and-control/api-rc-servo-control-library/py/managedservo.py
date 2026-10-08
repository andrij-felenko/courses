import pigpio

class ManagedServo:
    def __init__(self, pin, host='localhost', port=8888):
        self.pin = pin
        self.pi = pigpio.pi(host, port)

    def __enter__(self):
        if not self.pi.connected:
            raise RuntimeError("Не вдалося підключитися до демона pigpio")
        return self

    def set_pulse(self, us):
        self.pi.set_servo_pulsewidth(self.pin, us)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Гарантоване зняття сигналу та закриття сокета
        self.pi.set_servo_pulsewidth(self.pin, 0)
        self.pi.stop()
