import argparse
from crypto_keys import KeyGenerator
from efuse_ops import EfuseController

class EfuseProvisioner:
    """Координує весь процес прувіжнінгу: від перевірки чипа до запису ключів і накладання захисних масок."""
    
    def __init__(self, port: str):
        self.controller = EfuseController(port)
        self.key_gen = KeyGenerator()

    def provision_secure_boot(self):
        """Автоматизує процес підготовки пристрою до використання Secure Boot v2."""
        print("=== Початок апаратного прувіжнінгу ESP32-S3 ===")
        
        # 1. Вимкнення JTAG для захисту від відлагодження
        self.controller.disable_jtag()

        # 2. Перевірка доступності блоку для збереження ключа Secure Boot
        block = "BLOCK4" # Для Secure Boot зазвичай виділяється один з блоків KEYx
        if not self.controller.read_block_state(block):
            print(f"Помилка: {block} вже запрограмований або заблокований! Прувіжнінг неможливий.")
            return

        # 3. Генерація безпечного 256-бітного ключа
        sb_key = self.key_gen.generate_256bit_key()
        print(f"Згенеровано ключ Secure Boot (hex): {self.key_gen.format_key_hex(sb_key)}")

        # 4. Запис ключа в eFuse та встановлення його призначення
        self.controller.write_key_to_block(block, sb_key, "SECURE_BOOT_DIGEST0")

        # 5. Застосування read/write protection для блоку
        self.controller.set_read_write_protection(block)

        print("=== Прувіжнінг успішно завершено. Чип переведено в безпечний стан ===")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Утиліта прувіжнінгу eFuse та апаратних режимів завантаження ESP32-S3")
    parser.add_argument("--port", default="/dev/ttyUSB0", help="Послідовний порт для взаємодії з ESP32-S3")
    args = parser.parse_args()

    provisioner = EfuseProvisioner(args.port)
    provisioner.provision_secure_boot()
