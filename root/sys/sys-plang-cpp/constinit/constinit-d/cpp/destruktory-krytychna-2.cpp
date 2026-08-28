struct SafeRegistryGuard {
    bool active;
    constexpr SafeRegistryGuard() : active(true) {}
    
    ~SafeRegistryGuard() {
        // Нетривіальний деструктор коректно виконається при завершенні процесу!
        if (active) {
            flush_system_logs();
        }
    }
};

// ПОВНІСТЮ КОРЕКТНО: константний старт + коректне динамічне завершення
constinit SafeRegistryGuard g_guard{};
