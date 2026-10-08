# Обчислення калібрування та перетворення вибірок мовою Python
import math

class INA219Math:
    @staticmethod
    def compute_calibration(r_shunt: float, max_current: float):
        min_lsb = max_current / 32768.0
        current_lsb = math.ceil(min_lsb * 10000.0) / 10000.0
        power_lsb = 20.0 * current_lsb
        cal_value = int(math.trunc(0.04096 / (current_lsb * r_shunt)))
        return current_lsb, power_lsb, cal_value

    @staticmethod
    def bus_raw_to_volts(bus_reg: int) -> float:
        return (bus_reg >> 3) * 0.004

    @staticmethod
    def current_raw_to_amps(current_reg: int, current_lsb: float) -> float:
        # Обробка знака для 16-бітного доповняльного коду
        if current_reg > 32767:
            current_reg -= 65536
        return current_reg * current_lsb
