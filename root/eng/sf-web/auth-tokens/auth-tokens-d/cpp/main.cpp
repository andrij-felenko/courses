#include <string>
#include <chrono>
#include <mutex>
#include <condition_variable>
#include <optional>
#include <stdexcept>
#include <thread>

struct TokenData {
    std::string access_token;
    std::string refresh_token;
    std::chrono::system_clock::time_point expires_at;
};

class CppAuthInterceptor {
public:
    explicit CppAuthInterceptor(std::chrono::seconds skew = std::chrono::seconds(30))
        : skew_(skew), is_refreshing_(false) {}

    void set_tokens(std::string access, std::string refresh, std::chrono::seconds expires_in) {
        std::lock_guard<std::mutex> guard(mutex_);
        data_ = TokenData{
            std::move(access),
            std::move(refresh),
            std::chrono::system_clock::now() + expires_in
        };
    }

    [[nodiscard]] std::string get_valid_token() {
        std::string active_refresh;

        {
            std::unique_lock<std::mutex> lock(mutex_);
            while (true) {
                if (!data_.has_value()) {
                    throw std::runtime_error("Облікові дані відсутні");
                }

                auto now = std::chrono::system_clock::now();
                bool expired = (now >= (data_->expires_at - skew_));

                if (!expired) {
                    return data_->access_token;
                }

                if (!is_refreshing_) {
                    is_refreshing_ = true;
                    active_refresh = data_->refresh_token;
                    break;
                }
                cv_.wait(lock);
            }
        }

        try {
            TokenData fresh = execute_network_refresh(active_refresh);

            std::lock_guard<std::mutex> guard(mutex_);
            data_ = std::move(fresh);
            is_refreshing_ = false;
            cv_.notify_all();
            return data_->access_token;
        } catch (...) {
            std::lock_guard<std::mutex> guard(mutex_);
            is_refreshing_ = false;
            cv_.notify_all();
            throw;
        }
    }

private:
    static TokenData execute_network_refresh(const std::string& refresh) {
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
        auto now = std::chrono::system_clock::now();
        return TokenData{
            "cpp_acc_" + std::to_string(now.time_since_epoch().count()),
            "cpp_ref_" + std::to_string(now.time_since_epoch().count()),
            now + std::chrono::seconds(900)
        };
    }

    std::chrono::seconds skew_;
    std::optional<TokenData> data_;
    bool is_refreshing_;
    std::mutex mutex_;
    std::condition_variable cv_;
};
