import time

class VisaReader:
    def __init__(self, resource_string: str):
        self.resource_string = resource_string
        self.connected = False

    def connect(self):
        # Імітація підключення через PyVISA
        if not self.resource_string:
            raise ValueError("Не вказано адресу VISA ресурсу.")
        time.sleep(0.1)
        self.connected = True

    def disconnect(self):
        self.connected = False

    def read_waveforms(self):
        if not self.connected:
            raise ConnectionError("Немає з'єднання з приладом VISA.")
        
        # Генеруємо синтезовані вимірювальні дані для демонстрації (синусоїдальні коливання тиску і потоку)
        import math
        num_points = 1000
        time_data = [i / 10000.0 for i in range(num_points)] # 0.1 секунди
        
        # Частота 100 Гц
        f = 100.0
        pressure_data = [100.0 * math.sin(2 * math.pi * f * t) for t in time_data]
        # Потік з невеликою затримкою (фазовим зсувом) та зворотним викидом
        flow_data = [50.0 * math.sin(2 * math.pi * f * t - 0.3) - 5.0 * max(0, math.sin(2 * math.pi * f * t)) for t in time_data]
        
        return time_data, pressure_data, flow_data
