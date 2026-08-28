#include <iostream>
#include <thread>
#include <exception>
#include <stdexcept>

void worker_function(std::exception_ptr& err_out) {
    try {
        // Імітація обчислювальної помилки
        throw std::invalid_argument("Некоректний параметр у робочому потоці");
    } catch (...) {
        // Захоплюємо поточний виняток у потокобезпечний вказівник
        err_out = std::current_exception();
    }
}

void run_thread_with_exception_handling() {
    std::exception_ptr thread_error = nullptr;

    std::jthread t([&thread_error]() {
        worker_function(thread_error);
    });

    t.join(); // Очікуємо завершення потоку

    // Перевіряємо, чи був виняток у робочому потоці
    if (thread_error) {
        std::cout << "Перехоплено виняток з робочого потоку у головному потоці!\n";
        // Повторно викидаємо збережений виняток у контексті головного потоку
        std::rethrow_exception(thread_error);
    }
}
