// Концептуальна структура stop_state у runtime
struct stop_state {
    // Пакування лічильників та прапорців в одне 64-бітне атомарне слово
    // [1 біт: stop_requested] [1 біт: locked] [31 біт: source_count] [31 біт: token_count]
    std::atomic<uint64_t> state_flags_{0};

    // Ідентифікатор потоку, який наразі виконує request_stop()
    std::atomic<std::thread::id> executing_thread_{};

    // Вказівник на початок зв'язного списку зареєстрованих об'єктів stop_callback
    stop_callback_base* head_callback_{nullptr};

    // М'ютекс або атомарний спінлок для захисту операцій вставки/видалення зі списку
    std::atomic_flag list_lock_ = ATOMIC_FLAG_INIT;
};
