#pragma once

#include "temperature_core.hpp"

#include <iomanip>
#include <iostream>
#include <memory>
#include <optional>
#include <string>
#include <string_view>
#include <vector>

// ============================================================================
// ТОНКИЙ АДАПТЕР КОМАНДНОГО РЯДКА (DRIVING ADAPTER)
// ============================================================================

/// @brief Драйвуючий адаптер термінала CLI: розбирає аргументи командного рядка,
/// викликає вхідний порт ядра та транслює результати в коди виходу процесу (0, 1, 2).
class CliTemperatureAdapter {
public:
    // Стандартні POSIX-коди завершення процесу:
    static constexpr int kExitSuccess = 0;     ///< Успішне виконання (EX_OK)
    static constexpr int kExitDomainError = 1; ///< Порушення доменних правил бізнес-ядра
    static constexpr int kExitUsageError = 2;  ///< Помилка синтаксису аргументів (EX_USAGE)

    explicit CliTemperatureAdapter(std::shared_ptr<ISetTemperatureUseCase> use_case)
        : use_case_(std::move(use_case)) {}

    /// @brief Запуск адаптера з вектором рядкових аргументів.
    int run(const std::vector<std::string>& args, 
            std::ostream& out = std::cout, 
            std::ostream& err = std::cerr) const {
        // Обробка запиту довідки
        for (const auto& arg : args) {
            if (arg == "--help" || arg == "-h") {
                print_help(out);
                return kExitSuccess;
            }
        }

        // 1. Синтаксичний розбір прапорців консолі
        std::optional<std::string> zone_id;
        std::optional<double> target_temperature;
        std::optional<std::string> user_id;

        for (size_t i = 0; i < args.size(); ++i) {
            const auto& arg = args[i];
            if (arg == "--zone" || arg == "-z") {
                if (i + 1 < args.size()) zone_id = args[++i];
                else return fail_usage("Прапорець --zone потребує значення", err);
            } else if (arg == "--temp" || arg == "-t") {
                if (i + 1 < args.size()) {
                    try {
                        target_temperature = std::stod(args[++i]);
                    } catch (...) {
                        return fail_usage("Значення --temp має бути дійсним числом", err);
                    }
                } else {
                    return fail_usage("Прапорець --temp потребує числового значення", err);
                }
            } else if (arg == "--user" || arg == "-u") {
                if (i + 1 < args.size()) user_id = args[++i];
                else return fail_usage("Прапорець --user потребує значення", err);
            } else {
                return fail_usage("Невідомий аргумент: " + arg, err);
            }
        }

        // Валідація наявності всіх обов'язкових аргументів
        if (!zone_id.has_value() || !target_temperature.has_value() || !user_id.has_value()) {
            return fail_usage("Відсутні обов'язкові прапорці. Потрібно вказати: --zone, --temp, --user", err);
        }

        // 2. Формування незмінного Command DTO ядра
        SetTemperatureCommand command(*zone_id, *target_temperature, *user_id);

        // 3. Виклик вхідного порту
        auto result = use_case_->execute(command);

        // 4. Трансляція вердикту ядра в POSIX-коди виходу та текстові повідомлення
        if (result) {
            out << std::fixed << std::setprecision(1);
            out << "[CLI OK] Зону '" << result->zone_id 
                << "' успішно налаштовано на " << result->new_temperature << "°C "
                << "(попереднє значення: " << result->previous_temperature << "°C)\n";
            return kExitSuccess; // 0
        }

        // Доменна помилка ядра транслюється в код виходу 1
        err << "[CLI DomainError] Помилка виконання бізнес-правила: " 
            << to_string(result.error()) << "\n";
        return kExitDomainError; // 1
    }

    /// @brief Зручний запуск із традиційними параметрами argc/argv функції main().
    int run(int argc, const char* const argv[], 
            std::ostream& out = std::cout, 
            std::ostream& err = std::cerr) const {
        std::vector<std::string> args;
        args.reserve(static_cast<size_t>(argc > 0 ? argc - 1 : 0));
        for (int i = 1; i < argc; ++i) {
            args.emplace_back(argv[i]);
        }
        return run(args, out, err);
    }

private:
    int fail_usage(const std::string& message, std::ostream& err) const {
        err << "[CLI UsageError] " << message << "\n";
        err << "Використання: cli_app --zone <id> --temp <градуси> --user <id>\n";
        return kExitUsageError; // 2
    }

    void print_help(std::ostream& out) const {
        out << "Кліматичний CLI-термінал керування термостатами\n"
            << "Параметри:\n"
            << "  -z, --zone <ідентифікатор>  Назва кліматичної зони\n"
            << "  -t, --temp <температура>    Цільова температура в градусах Цельсія\n"
            << "  -u, --user <користувач>     Ідентифікатор оператора або 'admin'\n"
            << "  -h, --help                  Показати цю довідку\n";
    }

    std::shared_ptr<ISetTemperatureUseCase> use_case_;
};
