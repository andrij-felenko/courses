class jthread {
public:
    // Конструктор створює внутрішній stop_source
    template<class Function, class... Args>
    explicit jthread(Function&& f, Args&&... args);

    // Деструктор: автоматичне скасування та приєднання
    ~jthread() {
        if (joinable()) {
            request_stop(); // 1. Надсилає сигнал скасування
            join();         // 2. Очікує завершення потоку
        }
    }

    [[nodiscard]] stop_source get_stop_source() noexcept;
    [[nodiscard]] stop_token get_stop_token() const noexcept;
    bool request_stop() noexcept;
};
