#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <filesystem>
#include <expected>
#include <system_error>
#include <algorithm>

namespace fs = std::filesystem;

class SysctlManager {
private:
    static constexpr std::string_view sysctl_prefix = "/proc/sys/";

public:
    // Трансляція ключа "net.ipv4.ip_forward" у fs::path "/proc/sys/net/ipv4/ip_forward"
    static std::expected<fs::path, std::string> key_to_path(std::string_view key) {
        std::string rel_path(key);
        std::replace(rel_path.begin(), rel_path.end(), '.', '/');

        fs::path full_path = fs::path(sysctl_prefix) / rel_path;
        return full_path;
    }

    // Зчитування значення параметра
    static std::expected<std::string, std::string> read_value(std::string_view key) {
        auto path_res = key_to_path(key);
        if (!path_res) {
            return std::unexpected(path_res.error());
        }

        const fs::path& path = *path_res;
        if (!fs::exists(path)) {
            return std::unexpected("Параметр не існує у /proc/sys: " + path.string());
        }

        std::ifstream file(path);
        if (!file.is_open()) {
            return std::unexpected("Не вдалося відкрити файл для читання: " + path.string() +
                                   " (перевірте права доступу)");
        }

        std::string value;
        if (std::getline(file, value)) {
            return value;
        }

        return std::unexpected("Не вдалося прочитати дані з файлу: " + path.string());
    }

    // Запис нового значення у параметр з автоматичним закриттям дескриптора (RAII)
    static std::expected<void, std::string> write_value(std::string_view key, std::string_view value) {
        auto path_res = key_to_path(key);
        if (!path_res) {
            return std::unexpected(path_res.error());
        }

        const fs::path& path = *path_res;
        if (!fs::exists(path)) {
            return std::unexpected("Параметр не існує у /proc/sys: " + path.string());
        }

        std::ofstream file(path);
        if (!file.is_open()) {
            return std::unexpected("Помилка доступу до " + path.string() +
                                   ": потрібні привілеї root (CAP_SYS_ADMIN або CAP_NET_ADMIN)");
        }

        file << value;
        if (!file.good()) {
            return std::unexpected("Помилка запису даних у " + path.string() +
                                   " (можливо, значення поза допустимим діапазоном)");
        }

        return {};
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <ключ> [значення]\n";
        std::cerr << "Приклад читання: " << argv[0] << " vm.swappiness\n";
        std::cerr << "Приклад запису:   " << argv[0] << " vm.swappiness 10\n";
        return 1;
    }

    std::string_view key = argv[1];

    if (argc == 2) {
        auto result = SysctlManager::read_value(key);
        if (result) {
            std::cout << key << " = " << *result << "\n";
            return 0;
        } else {
            std::cerr << "Помилка: " << result.error() << "\n";
            return 1;
        }
    } else {
        std::string_view value = argv[2];
        auto result = SysctlManager::write_value(key, value);
        if (result) {
            std::cout << key << " = " << value << "\n";
            return 0;
        } else {
            std::cerr << "Помилка: " << result.error() << "\n";
            return 1;
        }
    }
}
