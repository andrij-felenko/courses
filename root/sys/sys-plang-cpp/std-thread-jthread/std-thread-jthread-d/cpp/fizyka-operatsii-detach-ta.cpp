void start_background_logging() {
    int local_buffer_size = 1024;
    std::string log_file = "app.log";

    std::thread t([&local_buffer_size, &log_file]() {
        // Затримка виконання
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        // КАТАСТРОФА! local_buffer_size та log_file вже знищені на стеку!
        std::cout << "Logging to " << log_file << " buffer: " << local_buffer_size << "\n";
    });

    t.detach(); // Потік від'єднано, функція повертає управління негайно
} // Стек функції start_background_logging знищується! UB у фоновому потоці!
