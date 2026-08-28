#include <iostream>
#include <fstream>
#include <string>
#include <optional>

// Читання поточного значення ліміту відкритих файлів ядра через C++ RAII
std::optional<long long> getKernelMaxFiles() {
    std::ifstream file("/proc/sys/fs/file-max");
    if (!file.is_open()) {
        return std::nullopt;
    }

    long long max_files = 0;
    if (file >> max_files) {
        return max_files;
    }
    return std::nullopt;
}
