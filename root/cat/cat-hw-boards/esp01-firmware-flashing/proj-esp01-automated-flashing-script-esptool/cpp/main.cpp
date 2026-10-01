#include "flasher.hpp"
#include <iostream>
#include <fstream>
#include <vector>

int main(int argc, char* argv[]) {
    std::cout << "==================================================" << std::endl;
    std::cout << "  Кросплатформний прошивач ESP-01 / ESP8266 (C++)" << std::endl;
    std::cout << "==================================================" << std::endl;

    if (argc < 3) {
        std::cout << "Використання: " << argv[0] << " <COM-порт/девайс> <шлях_до_firmware.bin> [адреса_hex]" << std::endl;
        std::cout << "Приклад:    " << argv[0] << " COM3 firmware.bin 0x00000" << std::endl;
        return 1;
    }

    std::string port = argv[1];
    std::string filepath = argv[2];
    uint32_t address = 0x00000;

    if (argc >= 4) {
        address = std::stoul(argv[3], nullptr, 16);
    }

    std::ifstream file(filepath, std::ios::binary | std::ios::ate);
    if (!file.is_open()) {
        std::cerr << "[ERROR] Не вдалося відкрити файл прошивки: " << filepath << std::endl;
        return 1;
    }

    std::streamsize size = file.tellg();
    file.seekg(0, std::ios::beg);

    std::vector<uint8_t> buffer(size);
    if (!file.read(reinterpret_cast<char*>(buffer.data()), size)) {
        std::cerr << "[ERROR] Помилка читання даних з файла!" << std::endl;
        return 1;
    }

    std::cout << "[INFO] Файл " << filepath << " завантажено (" << size << " байт)." << std::endl;
    std::cout << "[INFO] Підключення до порту " << port << "..." << std::endl;

    EspFlasher flasher(port, 115200);
    if (!flasher.open_port()) {
        std::cerr << "[ERROR] Не вдалося відкрити порт " << port << ". Перевірте підключення." << std::endl;
        return 1;
    }

    std::cout << "[INFO] Виконання автоскидання у завантажувач (DTR/RTS)..." << std::endl;
    if (!flasher.sync_bootloader()) {
        std::cerr << "[ERROR] Збій синхронізації з ROM Bootloader! Перевірте підтяжки GPIO0/RST." << std::endl;
        return 1;
    }

    std::cout << "[INFO] Рукостискання успішне! Початок програмування Flash..." << std::endl;
    if (!flasher.write_flash(address, buffer)) {
        std::cerr << "[ERROR] Збій під час запису прошивки!" << std::endl;
        return 1;
    }

    return 0;
}
