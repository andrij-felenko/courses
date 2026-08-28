#include <iostream>
#include <fstream>
#include <string>
#include <filesystem>
#include <string_view>

namespace fs = std::filesystem;

class RaidReshapeMonitor {
public:
    explicit RaidReshapeMonitor(std::string device_name)
        : device_name_(std::move(device_name)) {}

    bool inspect_status() const {
        const fs::path sysfs_base = fs::path("/sys/block") / device_name_ / "md";
        
        if (!fs::exists(sysfs_base)) {
            std::cerr << "Помилка: каталог " << sysfs_base << " не існує в системі\n";
            return false;
        }

        const std::string action = query_sysfs_attribute(sysfs_base / "sync_action");
        if (action != "reshape") {
            std::cout << "Масив " << device_name_ 
                      << " не перебудовується (стан: " << action << ")\n";
            return true;
        }

        const std::string completed = query_sysfs_attribute(sysfs_base / "sync_completed");
        const std::string speed = query_sysfs_attribute(sysfs_base / "sync_speed");
        const std::string direction = query_sysfs_attribute(sysfs_base / "reshape_direction");

        std::cout << "Стан масиву " << device_name_ << ": активна перебудова (reshape)\n";
        std::cout << "  Напрямок руху смуг  : " << (direction.empty() ? "невідомо" : direction) << "\n";
        std::cout << "  Прогрес у секторах  : " << completed << "\n";
        std::cout << "  Поточна швидкість   : " << speed << " КіБ/с\n";
        return true;
    }

private:
    std::string device_name_;

    static std::string query_sysfs_attribute(const fs::path &attribute_path) {
        std::ifstream file_stream(attribute_path);
        if (!file_stream.is_open()) {
            return "";
        }
        std::string line_content;
        std::getline(file_stream, line_content);
        return line_content;
    }
};

int main(int argc, char *argv[]) {
    const std::string target_device = (argc > 1) ? argv[1] : "md0";
    const RaidReshapeMonitor monitor(target_device);
    return monitor.inspect_status() ? 0 : 1;
}
