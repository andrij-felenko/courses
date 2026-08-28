#include <iostream>
#include <stdexcept>
#include <string>
#include <system_error>
#include <source_location>
#include <stacktrace>
#include <exception>

// Базовий доменний виняток розподіленого сховища даних
class storage_exception : public std::runtime_error {
private:
    std::error_code code_;
    std::source_location location_;
    std::stacktrace trace_;
    mutable std::string formatted_what_;

public:
    // Конструктор із підтримкою error_code, source_location та stacktrace
    explicit storage_exception(
        std::error_code ec,
        const std::string& message,
        std::source_location loc = std::source_location::current(),
        std::stacktrace trace = std::stacktrace::current()
    ) : std::runtime_error(message),
        code_(ec),
        location_(loc),
        trace_(std::move(trace)) {}

    // Доступ до системного коду помилки
    [[nodiscard]] const std::error_code& code() const noexcept {
        return code_;
    }

    // Доступ до точки генерації у вихідному коді
    [[nodiscard]] const std::source_location& location() const noexcept {
        return location_;
    }

    // Доступ до знімку стеку викликів
    [[nodiscard]] const std::stacktrace& trace() const noexcept {
        return trace_;
    }

    // Перекритий поліморфний метод what() з ледачим форматуванням
    [[nodiscard]] const char* what() const noexcept override {
        if (formatted_what_.empty()) {
            try {
                formatted_what_ = std::string(std::runtime_error::what()) +
                    "\n  [Помилка]: " + code_.category().name() + ":" + std::to_string(code_.value()) +
                    " (" + code_.message() + ")" +
                    "\n  [Локація]: " + location_.file_name() + ":" +
                    std::to_string(location_.line()) + " in " + location_.function_name();
            } catch (...) {
                return std::runtime_error::what();
            }
        }
        return formatted_what_.c_str();
    }
};

// Спеціалізований виняток мережевого I/O
class network_io_exception : public storage_exception {
private:
    std::string remote_endpoint_;

public:
    network_io_exception(
        std::error_code ec,
        std::string endpoint,
        const std::string& msg,
        std::source_location loc = std::source_location::current()
    ) : storage_exception(ec, msg + " [Endpoint: " + endpoint + "]", loc),
        remote_endpoint_(std::move(endpoint)) {}

    [[nodiscard]] const std::string& endpoint() const noexcept {
        return remote_endpoint_;
    }
};

// Приклад використання та демонстрація вкладених винятків
void low_level_network_read(const std::string& host) {
    // Імітація системного збою ECONNRESET (Connection reset by peer)
    std::error_code ec(104, std::generic_category());
    throw network_io_exception(ec, host + ":8080", "Помилка читання із сокета");
}

void process_client_request(const std::string& host) {
    try {
        low_level_network_read(host);
    } catch (...) {
        // Загортаємо низькорівневу мережеву помилку у виняток бізнес-логіки
        std::throw_with_nested(
            storage_exception(
                std::make_error_code(std::errc::io_error),
                "Не вдалося виконати транзакцію клієнта"
            )
        );
    }
}

int main() {
    try {
        process_client_request("192.168.1.50");
    } catch (const storage_exception& e) {
        std::cout << "=== ПЕРЕХОПЛЕНО ДОМЕННИЙ ВИНЯТОК ===" << std::endl;
        std::cout << e.what() << std::endl;

        // Друк стеку викликів (якщо підтримується платформою)
        if (!e.trace().empty()) {
            std::cout << "\n=== СТЕК ВИКЛИКІВ (STACKTRACE) ===" << std::endl;
            std::cout << std::to_string(e.trace()) << std::endl;
        }

        // Перевірка на наявність вкладеного винятку
        try {
            std::rethrow_if_nested(e);
        } catch (const network_io_exception& nested) {
            std::cout << "\n=== ПРИЧИННИЙ ВКЛАДЕНИЙ ВИНЯТОК ===" << std::endl;
            std::cout << "Вузол: " << nested.endpoint() << std::endl;
            std::cout << "Код: " << nested.code().value() << std::endl;
        } catch (...) {
            std::cout << "\nПерехоплено невідомий вкладений виняток." << std::endl;
        }
    }
    return 0;
}
