// Рівень 1: Глобальний простір
void log_event(long x) { std::cout << "Global long: " << x << '\n'; }

// Рівень 2: Простір імен сервісів
namespace SystemServices {
    void log_event(const char* s) { std::cout << "SystemServices string: " << s << '\n'; }

    // Рівень 3: Базовий клас
    struct BaseHandler {
        void log_event(double d) { std::cout << "Base double: " << d << '\n'; }
    };

    // Рівень 4: Похідний клас
    struct CustomHandler : public BaseHandler {
        using BaseHandler::log_event; // втягуємо BaseHandler::log_event(double)
        void log_event(std::string_view sv) { std::cout << "Custom string_view: " << sv << '\n'; }

        // Рівень 5: Локальний метод
        void run() {
            log_event("hello"); // Виклик А
            log_event(3.14);    // Виклик Б
            log_event(100L);    // Виклик В
        }
    };
}
