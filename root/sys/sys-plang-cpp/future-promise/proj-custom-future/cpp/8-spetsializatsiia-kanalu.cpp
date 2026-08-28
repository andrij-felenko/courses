template <>
struct shared_state<void> {
    std::mutex mtx;
    std::condition_variable cv;
    bool ready = false;
    std::exception_ptr exception; // Значення T відсутнє, зберігається лише виняток
};

template <>
class custom_promise<void> {
public:
    void set_value() {
        std::unique_lock<std::mutex> lock(state_->mtx);
        if (state_->ready) throw std::logic_error("promise_already_satisfied");
        state_->ready = true;
        lock.unlock();
        state_->cv.notify_all();
    }
    // інші методи аналогічні
};
