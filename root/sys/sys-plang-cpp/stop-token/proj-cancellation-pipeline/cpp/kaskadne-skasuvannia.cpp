#include <functional>
#include <stop_token>

class CascadingStageController {
public:
    explicit CascadingStageController(std::stop_token parent_token)
        : parent_token_(parent_token),
          // Реєструємо підписку: якщо батьківське джерело скасовано,
          // ми негайно транслюємо сигнал у наше локальне джерело стадії
          parent_callback_(parent_token_, [this] {
              local_stop_source_.request_stop();
          }) {}

    // Локальне скасування лише цієї підсистеми
    void cancel_stage() {
        local_stop_source_.request_stop();
    }

    [[nodiscard]] std::stop_token get_stage_token() const noexcept {
        return local_stop_source_.get_token();
    }

private:
    std::stop_token parent_token_;
    std::stop_source local_stop_source_;
    std::stop_callback<std::function<void()>> parent_callback_;
};
