#include <iostream>
#include <cassert>

int main() {
    std::cout << "=== ТЕСТУВАННЯ СИСТЕМНОГО ЛАУНЧЕРА (C++) ===\n\n";

    // Тест 1: Неіснуючий бінарний файл
    {
        ProcessConfigOptions opt;
        opt.executable = "nonexistent_command_12345";
        opt.argv = { "nonexistent_command_12345" };

        auto result = launch_process_cpp(opt);
        if (!result) {
            std::cout << "[Тест 1: Неіснуючий файл] Отримано очікувану помилку: "
                      << result.error().message() << " (код: " << result.error().value() << ")\n";
            assert(result.error() == std::errc::no_such_file_or_directory);
        }
    }

    // Тест 2: Успішний запуск
    {
        ProcessConfigOptions opt;
        opt.executable = "/bin/echo";
        opt.argv = { "echo", "Тест C++ успішний!" };

        auto result = launch_process_cpp(opt);
        if (result) {
            std::cout << "[Тест 2: Успішний запуск] Створено процес PID: " << *result << "\n";
            int status = 0;
            waitpid(*result, &status, 0);
            std::cout << "  -> Процес успішно виконався й повернув код " << WEXITSTATUS(status) << "\n";
        }
    }

    return 0;
}
