#include <chrono>
#include <condition_variable>
#include <mutex>
#include <stop_token>

class PeriodicWorker {
public:
    void run(std::stop_token stoken) {
        std::unique_lock lock(mutex_);
        while (!stoken.stop_requested()) {
            perform_heartbeat_sync();

            // Спимо 10 секунд АБО прокидаємося негайно, якщо викликано request_stop()
            cv_.wait_for(lock, stoken, std::chrono::seconds(10), [&stoken] {
                return stoken.stop_requested();
            });
        }
    }

private:
    void perform_heartbeat_sync() { /* відправка телеметрії */ }

    std::mutex mutex_;
    std::condition_variable_any cv_;
};
