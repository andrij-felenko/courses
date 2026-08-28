template <class Receiver>
class async_sleep_op_state {
public:
    // Сувора заборона копіювання та переміщення
    async_sleep_op_state(const async_sleep_op_state&) = delete;
    async_sleep_op_state& operator=(const async_sleep_op_state&) = delete;
    async_sleep_op_state(async_sleep_op_state&&) = delete;
    async_sleep_op_state& operator=(async_sleep_op_state&&) = delete;

    async_sleep_op_state(Receiver&& rcvr, timer_service& srv, std::chrono::milliseconds dur)
        : receiver_(std::forward<Receiver>(rcvr)),
          service_(srv),
          duration_(dur),
          completed_(false) {}

    // Метод запуску операції: гарантовано noexcept
    void start() noexcept {
        // 1. Перевірка, чи не було скасування надіслано до моменту запуску
        if (check_cancellation_precondition()) {
            exec_model::set_stopped(std::move(receiver_));
            return;
        }

        // 2. Реєстрація асинхронного таймера у фоновому сервісі
        try {
            service_.schedule_after(duration_, [this](bool cancelled) {
                // Атомарна перевірка: чи не було сигнал уже доставлено іншим шляхом
                bool expected = false;
                if (!completed_.compare_exchange_strong(expected, true)) {
                    return; // Сигнал уже надіслано
                }

                if (cancelled) {
                    exec_model::set_stopped(std::move(receiver_));
                } else {
                    // Успішне завершення: надсилаємо сигнал у канал set_value
                    exec_model::set_value(std::move(receiver_));
                }
            });
        } catch (...) {
            // У разі системної помилки реєстрації відправляємо виняток у канал set_error
            bool expected = false;
            if (completed_.compare_exchange_strong(expected, true)) {
                exec_model::set_error(std::move(receiver_), std::current_exception());
            }
        }
    }

private:
    bool check_cancellation_precondition() const noexcept {
        return false;
    }

    Receiver receiver_;
    timer_service& service_;
    std::chrono::milliseconds duration_;
    std::atomic<bool> completed_;
};
