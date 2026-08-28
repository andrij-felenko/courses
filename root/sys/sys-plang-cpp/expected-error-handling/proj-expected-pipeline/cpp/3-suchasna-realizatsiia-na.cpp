// Сучасний ідіоматичний C++23 конвеєр з std::expected та RAII
#include <expected>
#include <string>
#include <string_view>
#include <fstream>
#include <sstream>
#include <iostream>
#include <format>

// 1. Доменна ієрархія помилок
enum class ConfigError {
    FileNotFound,
    ReadFailed,
    InvalidFormat,
    InvalidPortRange,
    InvalidThreadCount
};

// Адаптер для форматованого виводу помилок
std::string_view to_string(ConfigError err) noexcept {
    switch (err) {
        case ConfigError::FileNotFound:       return "Файл не знайдено на диску";
        case ConfigError::ReadFailed:         return "Помилка читання даних з файлу";
        case ConfigError::InvalidFormat:       return "Некоректний синтаксис конфігурації";
        case ConfigError::InvalidPortRange:   return "Порт знаходиться поза діапазоном 1..65535";
        case ConfigError::InvalidThreadCount: return "Кількість потоків поза діапазоном 1..128";
    }
    return "Невідома помилка";
}

// 2. Ідіоматичні дані конфігурації
struct ServiceConfig {
    std::string db_host;
    int port;
    int worker_threads;
};

// 3. Зчитування файлу через RAII
std::expected<std::string, ConfigError> read_file_content(std::string_view path) {
    std::ifstream file(path.data(), std::ios::in | std::ios::binary);
    if (!file.is_open()) {
        return std::unexpected(ConfigError::FileNotFound);
    }

    std::ostringstream ss;
    ss << file.rdbuf();
    if (file.bad()) {
        return std::unexpected(ConfigError::ReadFailed);
    }

    return ss.str();
}

// 4. Парсинг конфігураційного рядка
std::expected<ServiceConfig, ConfigError> parse_config_raw(const std::string& content) {
    std::istringstream iss(content);
    std::string host;
    int port = 0;
    int threads = 0;

    if (!(iss >> host >> port >> threads)) {
        return std::unexpected(ConfigError::InvalidFormat);
    }

    return ServiceConfig{
        .db_host = std::move(host),
        .port = port,
        .worker_threads = threads
    };
}

// 5. Валідація бізнес-правил
std::expected<ServiceConfig, ConfigError> validate_config(ServiceConfig cfg) {
    if (cfg.port < 1 || cfg.port > 65535) {
        return std::unexpected(ConfigError::InvalidPortRange);
    }
    if (cfg.worker_threads < 1 || cfg.worker_threads > 128) {
        return std::unexpected(ConfigError::InvalidThreadCount);
    }
    return cfg; // Повертаємо виправлену та перевірену конфігурацію
}

// 6. Побудова елегантного монадичного конвеєра
std::expected<ServiceConfig, ConfigError> load_service_configuration(std::string_view path) {
    return read_file_content(path)
        .and_then(parse_config_raw)
        .and_then(validate_config);
}

// 7. Головний точці входу з відвідною обробкою
int main() {
    auto config_result = load_service_configuration("server_config.txt")
        .transform([](const ServiceConfig& cfg) {
            std::cout << std::format("Конфігурацію завантажено успішно! Host: {}, Port: {}, Threads: {}\n",
                                     cfg.db_host, cfg.port, cfg.worker_threads);
            return cfg;
        })
        .or_else([](ConfigError err) -> std::expected<ServiceConfig, ConfigError> {
            std::cerr << std::format("Критичний збій завантаження конфігурації: {}\n", to_string(err));
            // Відновлення за замовчуванням при відсутності файлу
            if (err == ConfigError::FileNotFound) {
                std::cout << "Застосовується резервна конфігурація за замовчуванням...\n";
                return ServiceConfig{"127.0.0.1", 8080, 4};
            }
            return std::unexpected(err);
        });

    if (config_result) {
        std::cout << "Сервіс готовий до запуску.\n";
    } else {
        std::cout << "Запуск сервісу скасовано через помилку.\n";
    }

    return 0;
}
