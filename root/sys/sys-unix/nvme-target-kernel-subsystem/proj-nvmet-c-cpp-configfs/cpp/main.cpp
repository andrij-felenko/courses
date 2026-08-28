#include <iostream>
#include <fstream>
#include <filesystem>
#include <string_view>
#include <system_error>
#include <utility>

namespace fs = std::filesystem;

// RAII-обгортка для автоматичного відкату конфігурації у разі винятків
class configfs_directory_guard {
public:
    explicit configfs_directory_guard(fs::path path) : path_(std::move(path)) {
        std::error_code ec;
        fs::create_directories(path_, ec);
        if (ec) {
            throw std::system_error(ec, "Не вдалося створити директорію configfs: " + path_.string());
        }
        created_ = true;
    }

    ~configfs_directory_guard() {
        if (created_) {
            std::error_code ec;
            fs::remove(path_, ec);
        }
    }

    // Відключення автоматичного вилучення після успішного виконання
    void dismiss() noexcept { created_ = false; }
    [[nodiscard]] const fs::path& path() const noexcept { return path_; }

private:
    fs::path path_;
    bool created_{false};
};

static void write_config_attribute(const fs::path& attr_path, std::string_view value) {
    std::ofstream ofs(attr_path);
    if (!ofs.is_open()) {
        throw std::runtime_error("Не вдалося відкрити атрибут: " + attr_path.string());
    }
    ofs << value << '\n';
    ofs.flush();  // без цього write() відклався б до закриття потоку — після перевірки
    if (!ofs.good()) {
        throw std::runtime_error("Помилка запису в атрибут: " + attr_path.string());
    }
}

int main() {
    try {
        const fs::path configfs_root = "/sys/kernel/config/nvmet";
        const std::string subsys_nqn = "nqn.2026-08.org.example:target-storage";

        std::cout << "Розпочинаємо конфігурацію NVMe Target через C++ RAII API...\n";

        // 1. Створення підсистеми з RAII захистом від збоїв
        configfs_directory_guard subsys_guard(configfs_root / "subsystems" / subsys_nqn);
        write_config_attribute(subsys_guard.path() / "attr_allow_any_host", "1");

        // 2. Створення та активація простору імен
        configfs_directory_guard ns_guard(subsys_guard.path() / "namespaces" / "1");
        write_config_attribute(ns_guard.path() / "device_path", "/dev/ram0");
        write_config_attribute(ns_guard.path() / "enable", "1");

        // 3. Створення мережевого порту
        configfs_directory_guard port_guard(configfs_root / "ports" / "1");
        write_config_attribute(port_guard.path() / "addr_trtype", "tcp");
        write_config_attribute(port_guard.path() / "addr_traddr", "192.168.1.50");
        write_config_attribute(port_guard.path() / "addr_trsvcid", "4420");
        write_config_attribute(port_guard.path() / "addr_adrfam", "ipv4");

        // 4. Створення символічного посилання прив'язки (Активація)
        const fs::path link_path = port_guard.path() / "subsystems" / subsys_nqn;
        std::error_code ec;
        fs::create_directory_symlink(subsys_guard.path(), link_path, ec);
        if (ec) {
            throw std::system_error(ec, "Не вдалося створити symlink прив'язки порту");
        }

        // У разі успіху скасовуємо автоматичне вилучення об'єктів у деструкторах
        port_guard.dismiss();
        ns_guard.dismiss();
        subsys_guard.dismiss();

        std::cout << "NVMe Target успішно сконфігуровано та запущено мовою C++ (RAII)!\n";
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка конфігурації: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
