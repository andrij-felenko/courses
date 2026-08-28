// userspace_suspend.cpp: ідіоматична обгортка RAII для безпечного сну
#include <iostream>
#include <fstream>
#include <string>
#include <system_error>
#include <expected>

class PowerManager {
public:
    static std::expected<void, std::error_code> trigger_safe_suspend() {
        std::string wakeup_count_str;

        // Крок 1. Читаємо актуальне значення лічильника
        {
            std::ifstream count_in("/sys/power/wakeup_count");
            if (!count_in.is_open()) {
                return std::unexpected(std::make_error_code(std::errc::no_such_file_or_directory));
            }
            if (!(count_in >> wakeup_count_str)) {
                return std::unexpected(std::make_error_code(std::errc::io_error));
            }
        }

        // Крок 2. Атомарно верифікуємо лічильник записом назад
        {
            std::ofstream count_out("/sys/power/wakeup_count");
            if (!count_out.is_open()) {
                return std::unexpected(std::make_error_code(std::errc::permission_denied));
            }
            count_out << wakeup_count_str;
            count_out.flush();
            if (count_out.fail()) {
                std::cerr << "Подію пробудження зафіксовано перед сном! Призупинення скасовано.\n";
                return std::unexpected(std::make_error_code(std::errc::invalid_argument));
            }
        }

        // Крок 3. Ініціюємо перехід у сон
        {
            std::ofstream state_out("/sys/power/state");
            if (!state_out.is_open()) {
                return std::unexpected(std::make_error_code(std::errc::permission_denied));
            }
            std::cout << "Перевірка успішна. Перехід у стан сну mem...\n";
            state_out << "mem\n";
            state_out.flush();
            if (state_out.fail()) {
                return std::unexpected(std::make_error_code(std::errc::io_error));
            }
        }

        std::cout << "Система успішно прокинулася зі стану сну.\n";
        return {};
    }
};

int main() {
    auto result = PowerManager::trigger_safe_suspend();
    if (!result) {
        std::cerr << "Помилка призупинення: " << result.error().message() << '\n';
        return 1;
    }
    return 0;
}
