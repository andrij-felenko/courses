// wmi_scan.cpp — Ідіоматична версія на C++20 (RAII, filesystem, iostreams)
#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <string_view>

namespace fs = std::filesystem;

class WmiScanner {
public:
    static constexpr std::string_view kSysfsWmiPath = "/sys/bus/wmi/devices";

    void scan() const {
        const fs::path wmi_dir{kSysfsWmiPath};
        if (!fs::exists(wmi_dir) || !fs::is_directory(wmi_dir)) {
            std::cerr << "Каталог " << wmi_dir << " не знайдено або доступ обмежено.\n";
            return;
        }

        std::cout << "=== Сканування WMI пристроїв Linux (C++20) ===\n";
        for (const auto& entry : fs::directory_iterator(wmi_dir)) {
            if (entry.is_directory() || entry.is_symlink()) {
                inspect_device(entry.path());
            }
        }
    }

private:
    void inspect_device(const fs::path& dev_path) const {
        const auto object_id_file = dev_path / "object_id";
        if (std::ifstream file{object_id_file}; file.is_open()) {
            std::string object_id;
            if (std::getline(file, object_id)) {
                std::cout << "WMI Device: " << dev_path.filename().string()
                          << " | Object ID: " << object_id << '\n';
            }
        }
    }
};

int main() {
    WmiScanner scanner;
    scanner.scan();
    return 0;
}
