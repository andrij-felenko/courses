template <class PrevOpState, class Func, class Receiver>
struct then_operation_state {
    PrevOpState prev_op_;       // Вкладений стан попередньої операції
    Func func_;                 // Збережена функція-трансформатор
    Receiver rcvr_;             // Приймач результату

    void start() noexcept {
        // Запуск попереднього кроку
        std::execution::start(prev_op_);
    }
};
