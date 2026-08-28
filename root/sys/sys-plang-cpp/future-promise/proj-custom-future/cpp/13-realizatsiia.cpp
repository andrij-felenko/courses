template <typename T>
void set_value_at_thread_exit_impl(custom_promise<T>& p, T val) {
    // Структура чистильника, деструктор якої викличеться при виході з потоку
    struct thread_exit_notifier {
        std::shared_ptr<shared_state<T>> state;
        T value;

        ~thread_exit_notifier() {
            if (state) {
                std::lock_guard<std::mutex> lock(state->mtx);
                state->storage = std::move(value);
                state->ready = true;
                state->cv.notify_all();
            }
        }
    };

    static thread_local thread_exit_notifier notifier;
    notifier.state = p.get_state_internal();
    notifier.value = std::move(val);
}
