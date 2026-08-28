#include <iostream>
#include <fstream>
#include <string>
#include <system_error>

bool is_kexec_loaded() {
    std::ifstream status_file("/sys/kernel/kexec_loaded");
    if (!status_file.is_open()) {
        throw std::system_error(errno, std::generic_category(), 
                                "Не вдалося відкрити /sys/kernel/kexec_loaded");
    }

    int value = 0;
    if (status_file >> value) {
        return value == 1;
    }
    
    return false;
}

int main() {
    try {
        bool loaded = is_kexec_loaded();
        std::cout << "Статус завантаження kexec: " << (loaded ? "Завантажено" : "Не завантажено") << "\n";
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
