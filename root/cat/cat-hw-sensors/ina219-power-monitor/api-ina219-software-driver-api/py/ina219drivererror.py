# Стійке зчитування даних з обробкою помилок мовою Python
import time

class INA219DriverError(Exception):
    pass

class INA219OverflowError(INA219DriverError):
    pass

class INA219CommunicationError(INA219DriverError):
    pass

class INA219Driver:
    def __init__(self, i2c_bus, address: int, current_lsb: float, power_lsb: float):
        self.bus = i2c_bus
        self.address = address
        self.current_lsb = current_lsb
        self.power_lsb = power_lsb

    def read_metrics_robust(self, retries: int = 3):
        for attempt in range(retries):
            try:
                bus_reg = self._read_register16(0x02)
                if bus_reg & 0x0001:
                    raise INA219OverflowError("Математичне переповнення АЦП/множника (OVF)")
                
                current_reg = self._read_register16(0x04)
                power_reg = self._read_register16(0x03)
                
                # Корекція знаку струму
                if current_reg > 32767:
                    current_reg -= 65536

                voltage = (bus_reg >> 3) * 0.004
                current = current_reg * self.current_lsb
                power = power_reg * self.power_lsb
                
                return voltage, current, power
            except OSError:
                if attempt == retries - 1:
                    raise INA219CommunicationError("Збій зв'язку по шині I2C після кількох спроб")
                time.sleep(0.01)

    def _read_register16(self, reg: int) -> int:
        # Імітація зчитування двох байтів
        return 0
