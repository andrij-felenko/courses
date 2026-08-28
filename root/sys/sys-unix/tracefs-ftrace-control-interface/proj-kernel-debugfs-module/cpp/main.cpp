#include <iostream>
#include <fstream>
#include <string>
#include <system_error>
#include <filesystem>

namespace fs = std::filesystem;

int main()
{
    const fs::path trace_pipe_path{"/sys/kernel/tracing/trace_pipe"};

    /*
     * Ідіоматичне відкриття файлового потоку в C++20
     * з використанням RAII для автоматичного закриття дескриптора.
     */
    std::ifstream trace_file{trace_pipe_path};
    if (!trace_file.is_open()) {
        std::cerr << "Помилка: не вдалося відкрити " << trace_pipe_path << '\n';
        std::cerr << "Перевірте права суперкористувача (sudo) та чи змонтовано /sys/kernel/tracing.\n";
        return 1;
    }

    std::cout << "=== Потокове зчитування tracefs (" << trace_pipe_path << ") ===\n";
    std::cout << "Натисніть Ctrl+C для зупинки.\n\n";

    std::string line;
    /*
     * Порядкове зчитування через std::getline.
     * Потік блокується ядром до появи нового рядка події у trace_pipe.
     */
    while (std::getline(trace_file, line)) {
        std::cout << line << '\n';
    }

    if (trace_file.bad()) {
        std::cerr << "Критична помилка потоку при зчитуванні з tracefs\n";
        return 1;
    }

    return 0;
}
