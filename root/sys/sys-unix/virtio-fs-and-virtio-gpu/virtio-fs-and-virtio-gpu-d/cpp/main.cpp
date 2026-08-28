#include <iostream>
#include <fstream>
#include <string>
#include <filesystem>

// Перевірка активності точок монтування virtiofs у procfs
void check_virtiofs_mounts() {
    std::ifstream mounts("/proc/mounts");
    std::string line;
    bool found = false;

    while (std::getline(mounts, line)) {
        if (line.find("virtiofs") != std::string::npos) {
            std::cout << "Знайдено точку монтування Virtio-FS: " << line << '\n';
            found = true;
        }
    }

    if (!found) {
        std::cout << "Точок монтування virtiofs не виявлено.\n";
    }
}
