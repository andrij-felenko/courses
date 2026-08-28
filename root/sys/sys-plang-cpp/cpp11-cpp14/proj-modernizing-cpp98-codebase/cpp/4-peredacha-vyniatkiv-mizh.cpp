#include <exception>
#include <stdexcept>
#include <iostream>

std::exception_ptr global_error = nullptr;

void background_worker() {
    try {
        // Симуляція критичної помилки обробки
        throw std::runtime_error("Помилка під час десеріалізації пакета");
    } catch (...) {
        // Захоплення поточного активного винятку без втрати типу
        global_error = std::current_exception();
    }
}

void check_worker_status() {
    if (global_error) {
        try {
            // Повторне збудження збереженого винятку в контексті головного потоку
            std::rethrow_exception(global_error);
        } catch (const std::exception& e) {
            std::cerr << "Перехоплено виняток з фонового потоку: " 
                      << e.what() << "\n";
        }
    }
}
