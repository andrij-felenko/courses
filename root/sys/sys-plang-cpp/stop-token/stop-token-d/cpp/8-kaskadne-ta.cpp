#include <functional>
#include <stop_token>

class HierarchicalTask {
public:
    explicit HierarchicalTask(std::stop_token parent_token)
        : parent_token_(parent_token),
          // Зв'язуємо батьківський токен із локальним джерелом:
          // якщо батьківський токен скасовується, ми автоматично скасовуємо локальне джерело
          parent_subscription_(parent_token_, [this] {
              local_source_.request_stop();
          }) {}

    // Локальне скасування лише цієї гілки
    void cancel_locally() {
        local_source_.request_stop();
    }

    [[nodiscard]] std::stop_token token() const noexcept {
        return local_source_.get_token();
    }

private:
    std::stop_token parent_token_;
    std::stop_source local_source_;
    std::stop_callback<std::function<void()>> parent_subscription_;
};
