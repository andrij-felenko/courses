// Утиліта керування configfs мовою C++ (C++20 std::filesystem & RAII)
#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <string_view>
#include <system_error>

namespace fs = std::filesystem;

class ConfigFsManager {
public:
    explicit ConfigFsManager(fs::path target_path) : path_(std::move(target_path)) {}

    bool create_object() {
        std::error_code ec;
        std::cout << "[C++] Створення об'єкта " << path_ << "...\n";
        if (fs::create_directory(path_, ec)) {
            std::cout << "[C++] Об'єкт успішно створено у ядрі.\n";
            return true;
        }
        if (ec) {
            std::cerr << "[C++] Помилка створення каталогу: " << ec.message() << "\n";
            return false;
        }
        return true;
    }

    bool write_attribute(std::string_view attr_name, std::string_view value) {
        fs::path attr_path = path_ / attr_name;
        std::ofstream ofs(attr_path);
        if (!ofs.is_open()) {
            std::cerr << "[C++] Не вдалося відкрити атрибут: " << attr_path << "\n";
            return false;
        }
        ofs << value;
        std::cout << "[C++] Записано значення '" << value << "' у " << attr_name << "\n";
        return ofs.good();
    }

    void print_attribute(std::string_view attr_name) const {
        fs::path attr_path = path_ / attr_name;
        std::ifstream ifs(attr_path);
        if (!ifs.is_open()) {
            std::cerr << "[C++] Не вдалося прочитати атрибут: " << attr_path << "\n";
            return;
        }
        std::string line;
        std::cout << "[C++] Зміст атрибута " << attr_name << ":\n";
        while (std::getline(ifs, line)) {
            std::cout << "  " << line << "\n";
        }
    }

    bool destroy_object() {
        std::error_code ec;
        std::cout << "[C++] Видалення об'єкта через rmdir " << path_ << "...\n";
        if (fs::remove(path_, ec)) {
            std::cout << "[C++] Об'єкт успішно знищено з ядра.\n";
            return true;
        }
        std::cerr << "[C++] Помилка видалення: " << ec.message() << "\n";
        return false;
    }

private:
    fs::path path_;
};

int main() {
    fs::path config_path = "/sys/kernel/config/demo_target/node_cpp";
    ConfigFsManager manager(config_path);

    if (!manager.create_object()) {
        return 1;
    }

    if (manager.write_attribute("value", "100")) {
        manager.print_attribute("status");
    }

    if (!manager.destroy_object()) {
        return 1;
    }

    return 0;
}
