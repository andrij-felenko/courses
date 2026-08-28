#include <mutex>
#include <condition_variable>
#include <memory>

class TokenRefreshCoordinator {
public:
    struct TokenBundle {
        std::string access_token;
        std::string refresh_token;
        int64_t expires_at{0};
    };

    // Отримання свіжого access_token з гарантією єдиного запиту до сервера
    std::string get_valid_access_token() {
        std::unique_lock<std::mutex> lock(mtx_);

        auto now = std::chrono::duration_cast<std::chrono::seconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();

        // Якщо токен ще дійсний щонайменше 30 секунд — віддаємо відразу
        if (tokens_.expires_at > (now + 30)) {
            return tokens_.access_token;
        }

        // Якщо інший потік уже виконує мережевий запит оновлення — очікуємо завершення
        if (refresh_in_progress_) {
            cv_.wait(lock, [this]() { return !refresh_in_progress_; });
            return tokens_.access_token;
        }

        // Цей потік бере на себе виконання оновлення
        refresh_in_progress_ = true;
        lock.unlock();

        try {
            TokenBundle fresh = execute_network_refresh(tokens_.refresh_token);

            lock.lock();
            tokens_ = fresh;
            refresh_in_progress_ = false;
            cv_.notify_all();
            return tokens_.access_token;
        } catch (...) {
            lock.lock();
            refresh_in_progress_ = false;
            cv_.notify_all();
            throw;
        }
    }

private:
    TokenBundle execute_network_refresh(const std::string& current_refresh_token) {
        // Тут виконується реальний мережевий HTTPS POST /token
        TokenBundle bundle;
        bundle.access_token = "eyJhbGciOiJSUzI1NiIs...";
        bundle.refresh_token = "r_new_rotated_string";
        bundle.expires_at = std::chrono::duration_cast<std::chrono::seconds>(
            std::chrono::system_clock::now().time_since_epoch()).count() + 3600;
        return bundle;
    }

    std::mutex mtx_;
    std::condition_variable cv_;
    bool refresh_in_progress_{false};
    TokenBundle tokens_;
};
