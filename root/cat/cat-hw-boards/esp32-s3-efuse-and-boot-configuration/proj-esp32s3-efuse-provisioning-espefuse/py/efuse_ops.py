class EfuseController:
    """Відповідає за читання регістрів eFuse, синдромне декодування та взаємодію з периферією."""
    
    def __init__(self, port: str):
        self.port = port
        # У реальному середовищі тут була б ініціалізація інструментів esptool або espsecure
        print(f"[EfuseController] Ініціалізація з'єднання на порту {port}")

    def read_block_state(self, block_name: str) -> bool:
        """Зчитує стан блоку eFuse. Повертає True, якщо блок порожній і готовий до запису."""
        print(f"[EfuseController] Зчитування стану системного блоку {block_name}...")
        # Імітація зчитування стану через послідовний порт
        return True

    def write_key_to_block(self, block_name: str, key: bytes, purpose: str):
        """Записує ключ у відповідний блок, застосовує кодування Reed-Solomon та встановлює призначення."""
        print(f"[EfuseController] Запис {len(key)*8}-бітного ключа в {block_name}.")
        print(f"[EfuseController] Встановлення KEY_PURPOSE = {purpose}.")
        print(f"[EfuseController] Застосування завадостійкого кодування Reed-Solomon.")

    def set_read_write_protection(self, block_name: str):
        """Встановлює незворотні біти захисту від читання та запису (read/write protection)."""
        print(f"[EfuseController] УВАГА: Встановлення блокування (read/write protection) для {block_name}. Дія незворотна!")

    def disable_jtag(self):
        """Вимкнення налагоджувальних інтерфейсів JTAG для запобігання апаратному злому."""
        print("[EfuseController] Прошивання біта eFuse для вимкнення інтерфейсу JTAG.")
