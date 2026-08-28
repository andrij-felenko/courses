#include <string>
#include <chrono>
#include <mutex>
#include <condition_variable>
#include <optional>
#include <stdexcept>
#include <thread>
#include <iostream>

struct TokenState {
    std::string access_token;
    std::string refresh_token;
    std::chrono::system_clock::time_point expires_at;
};

class AuthInterceptor {
public:
    explicit AuthInterceptor(std::chrono::seconds clock_skew = std::chrono::seconds(30))
        : clock_skew_(clock_skew), is_refreshing_(false) {}

    void set_tokens(std::string access_token, std::string refresh_token, std::chrono::seconds expires_in) {
        std::lock_guard<std::mutex> lock(mutex_);
        state_ = TokenState{
            std::move(access_token),
            std::move(refresh_token),
            std::chrono::system_clock::now() + expires_in
        };
    }

    [[nodiscard]] std::string get_valid_access_token() {
        std::string current_refresh_token;

        {
            std::unique_lock<std::mutex> lock(mutex_);
            while (true) {
                if (!state_.has_value()) {
                    throw std::runtime_error("Користувач не авторизований");
                }

                auto now = std::chrono::system_clock::now();
                bool is_expired = (now >= (state_->expires_at - clock_skew_));

                if (!is_expired) {
                    return state_->access_token;
                }

                if (!is_refreshing_) {
                    is_refreshing_ = true;
                    current_refresh_token = state_->refresh_token;
                    break;
                } else {
                    cv_.wait(lock);
                }
            }
        }

        // Оновлення виконується поза м'ютексом
        try {
            TokenState new_state = perform_network_refresh(current_refresh_token);

            std::lock_guard<std::mutex> lock(mutex_);
            state_ = std::move(new_state);
            is_refreshing_ = false;
            cv_.notify_all();
            return state_->access_token;
        } catch (...) {
            std::lock_guard<std::mutex> lock(mutex_);
            is_refreshing_ = false;
            cv_.notify_all();
            throw;
        }
    }

    [[nodiscard]] std::string handle_401(const std::string& failed_token) {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            if (state_.has_value() && state_->access_token != failed_token) {
                return state_->access_token; // Токен уже оновлено іншим потоком
            }
        }
        return get_valid_access_token();
    }

private:
    static TokenState perform_network_refresh(const std::string& refresh_token) {
        std::this_thread::sleep_for(std::chrono::milliseconds(50)); // Мережевий виклик
        auto now = std::chrono::system_clock::now();
        return TokenState{
            "cpp_access_token_" + std::to_string(now.time_since_epoch().count()),
            "cpp_refresh_token_" + std::to_string(now.time_since_epoch().count()),
            now + std::chrono::seconds(900)
        };
    }

    std::chrono::seconds clock_skew_;
    std::optional<TokenState> state_;
    bool is_refreshing_;
    std::mutex mutex_;
    std::condition_variable cv_;
};
