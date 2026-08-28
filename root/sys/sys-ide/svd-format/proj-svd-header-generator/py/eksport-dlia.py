# Приклад сгенерованого GDB PythonPrettyPrinter
class UsartStatusPrinter:
    """Pretty-printer для регістра USART_SR у консолі GDB."""
    def __init__(self, val):
        self.val = val

    def to_string(self):
        raw = int(self.val)
        flags = []
        if raw & (1 << 5): flags.append("RXNE(Готовий прийом)")
        if raw & (1 << 6): flags.append("TC(Передачу завершено)")
        if raw & (1 << 7): flags.append("TXE(Буфер порожній)")
        return f"0x{raw:08X} [{', '.join(flags)}]"
