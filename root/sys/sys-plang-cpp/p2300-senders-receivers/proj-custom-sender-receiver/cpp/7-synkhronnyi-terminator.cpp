template <class ValueType>
struct sync_wait_receiver {
    std::mutex& mtx;
    std::condition_variable& cv;
    bool& done;
    std::optional<ValueType>& storage;
    std::exception_ptr& error;
    bool& stopped;

    void set_value(ValueType val) noexcept {
        std::lock_guard<std::mutex> lock(mtx);
        storage.emplace(std::move(val));
        done = true;
        cv.notify_one();
    }

    void set_error(std::exception_ptr ex) noexcept {
        std::lock_guard<std::mutex> lock(mtx);
        error = ex;
        done = true;
        cv.notify_one();
    }

    void set_stopped() noexcept {
        std::lock_guard<std::mutex> lock(mtx);
        stopped = true;
        done = true;
        cv.notify_one();
    }
};

template <>
struct sync_wait_receiver<void> {
    std::mutex& mtx;
    std::condition_variable& cv;
    bool& done;
    std::exception_ptr& error;
    bool& stopped;

    void set_value() noexcept {
        std::lock_guard<std::mutex> lock(mtx);
        done = true;
        cv.notify_one();
    }

    void set_error(std::exception_ptr ex) noexcept {
        std::lock_guard<std::mutex> lock(mtx);
        error = ex;
        done = true;
        cv.notify_one();
    }

    void set_stopped() noexcept {
        std::lock_guard<std::mutex> lock(mtx);
        stopped = true;
        done = true;
        cv.notify_one();
    }
};

template <class Sender>
void run_sync_wait_pipeline(Sender&& snd) {
    std::mutex mtx;
    std::condition_variable cv;
    bool done = false;
    std::exception_ptr error = nullptr;
    bool stopped = false;

    sync_wait_receiver<void> rcvr{mtx, cv, done, error, stopped};
    auto op = exec_model::connect(std::forward<Sender>(snd), std::move(rcvr));
    exec_model::start(op);

    std::unique_lock<std::mutex> lock(mtx);
    cv.wait(lock, [&] { return done; });

    if (error) {
        std::rethrow_exception(error);
    }
    if (stopped) {
        std::cout << "[sync_wait] Операцію було скасовано." << std::endl;
    }
}

int main() {
    std::cout << "[Main] Ініціалізація сервісу таймерів..." << std::endl;
    timer_service srv;

    std::cout << "[Main] Складання ланцюжка без динамічних алокацій..." << std::endl;
    using namespace std::chrono_literals;

    // Формуємо складений асинхронний конвеєр
    auto pipeline = async_sleep(srv, 150ms)
                  | [] {
                        std::cout << "[Worker] Таймер 150мс спрацював успішно!" << std::endl;
                    }
                  | [] {
                        std::cout << "[Worker] Виконання другого кроку у конвеєрі." << std::endl;
                    };

    std::cout << "[Main] Запуск sync_wait (блокування стека main)..." << std::endl;
    run_sync_wait_pipeline(std::move(pipeline));

    std::cout << "[Main] Роботу конвеєра завершено штатно." << std::endl;
    return 0;
}
