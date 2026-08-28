#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <string_view>
#include <system_error>

namespace fs = std::filesystem;

struct ServerConfig {
    int log_level{1};
    std::string server_addr{"127.0.0.1"};
    int port{8080};
};

// Глобальний стан сервісу
static ServerConfig g_active_config;

void validate_config(const ServerConfig& cfg) {
    if (cfg.port <= 0 || cfg.port > 65535) {
        throw std::invalid_argument("Неприпустимий порт сервера");
    }
    if (cfg.server_addr.empty()) {
        throw std::invalid_argument("Порожня адреса сервера");
    }
}

void notify_subsystems(const ServerConfig& cfg) {
    // Симуляція сповіщення інших потоків або виділення пам'яті під мережевий сокет
    if (cfg.server_addr == "invalid.local") {
        throw std::runtime_error("Мережева підсистема відхилила нову адресу");
    }
}

void save_and_apply_config_cpp(const fs::path& target_path, const ServerConfig& new_cfg) {
    const fs::path tmp_path = target_path.string() + ".tmp";
    const fs::path bak_path = target_path.string() + ".bak";

    // 1. Запис даних у тимчасовий файл
    {
        std::ofstream out(tmp_path, std::ios::binary | std::ios::trunc);
        if (!out.is_open()) {
            throw std::runtime_error("Неможливо створити тимчасовий файл: " + tmp_path.string());
        }
        out << new_cfg.log_level << "\n"
            << new_cfg.server_addr << "\n"
            << new_cfg.port << "\n";
        out.flush();
    }

    // Охоронець 1: видалення тимчасового файлу у разі будь-якого збою
    auto remove_tmp_guard = make_scope_guard([&tmp_path] noexcept {
        std::error_code ec;
        fs::remove(tmp_path, ec);
    });

    // 2. Валідація структури налаштувань (може викинути виняток)
    validate_config(new_cfg);

    // 3. Створення резервної копії поточного конфігураційного файлу
    bool had_backup = false;
    if (fs::exists(target_path)) {
        fs::rename(target_path, bak_path);
        had_backup = true;
    }

    // Охоронець 2: повернення резервної копії, якщо щось зламається далі
    auto restore_bak_guard = make_scope_guard([&, had_backup] noexcept {
        if (had_backup) {
            std::error_code ec;
            fs::rename(bak_path, target_path, ec);
        }
    });

    // 4. Атомарна підміна основного файлу
    fs::rename(tmp_path, target_path);

    // Тимчасовий файл став основним, видаляти його як сміття більше не потрібно
    remove_tmp_guard.dismiss();

    // 5. Оновлення кешу налаштувань у пам'яті
    ServerConfig old_cache = g_active_config;
    g_active_config = new_cfg;

    // Охоронець 3: відновлення пам'яті у разі помилки в підсистемах
    auto restore_cache_guard = make_scope_guard([&old_cache] noexcept {
        g_active_config = std::move(old_cache);
    });

    // 6. Сповіщення підсистем процесу (може викинути виняток під час ініціалізації сокета)
    notify_subsystems(new_cfg);

    // Всі кроки пройшли успішно: скасовуємо відкати й прибираємо бекап
    restore_cache_guard.dismiss();
    restore_bak_guard.dismiss();

    if (had_backup) {
        std::error_code ec;
        fs::remove(bak_path, ec);
    }
}
