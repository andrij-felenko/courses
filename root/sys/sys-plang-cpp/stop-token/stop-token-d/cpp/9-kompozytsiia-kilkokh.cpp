#include <functional>
#include <stop_token>
#include <vector>

class StopTokenCombiner {
public:
    StopTokenCombiner() = default;

    // Додавання зовнішнього токена до композиції
    void add_token(std::stop_token stoken) {
        if (!stoken.stop_possible()) {
            return;
        }

        // Якщо токен уже скасовано — негайно активуємо наше джерело
        if (stoken.stop_requested()) {
            combined_source_.request_stop();
            return;
        }

        // Реєструємо підписку: скасування будь-якого вхідного токена
        // автоматично активує спільне вихідне джерело
        callbacks_.emplace_back(std::make_unique<std::stop_callback<std::function<void()>>>(
            stoken, 
            [this] { combined_source_.request_stop(); }
        ));
    }

    [[nodiscard]] std::stop_token get_token() const noexcept {
        return combined_source_.get_token();
    }

private:
    std::stop_source combined_source_;
    std::vector<std::unique_ptr<std::stop_callback<std::function<void()>>>> callbacks_;
};
