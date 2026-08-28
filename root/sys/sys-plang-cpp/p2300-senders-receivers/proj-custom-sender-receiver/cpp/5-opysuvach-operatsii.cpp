class async_sleep_sender {
public:
    // Декларація підтримуваних сигнатур завершення
    struct completion_signatures {};

    explicit async_sleep_sender(timer_service& srv, std::chrono::milliseconds dur)
        : service_(srv), duration_(dur) {}

    // Фаза зв'язування для rvalue (переміщення)
    template <class Receiver>
    async_sleep_op_state<std::decay_t<Receiver>> connect(Receiver&& rcvr) && {
        return async_sleep_op_state<std::decay_t<Receiver>>(
            std::forward<Receiver>(rcvr), service_, duration_);
    }

    // Фаза зв'язування для lvalue (копіювання опису)
    template <class Receiver>
    async_sleep_op_state<std::decay_t<Receiver>> connect(Receiver&& rcvr) const& {
        return async_sleep_op_state<std::decay_t<Receiver>>(
            std::forward<Receiver>(rcvr), service_, duration_);
    }

private:
    timer_service& service_;
    std::chrono::milliseconds duration_;
};

// Зручна функція-фабрика
inline async_sleep_sender async_sleep(timer_service& srv, std::chrono::milliseconds dur) {
    return async_sleep_sender(srv, dur);
}
