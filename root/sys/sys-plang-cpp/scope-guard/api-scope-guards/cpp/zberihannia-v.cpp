#include <optional>
#include <scope>

void conditional_guarded_operation(bool need_lock, Mutex& mtx) {
    // Відкладений охоронець: на початку порожній
    auto lock_guard = [&]() -> auto {
        if (need_lock) {
            mtx.lock();
            return std::optional(std::scope_exit([&mtx] noexcept { mtx.unlock(); }));
        }
        return std::optional<std::scope_exit<void(*)()>>{std::nullopt};
    }();

    // Виконання роботи...
    // Наприкінці блоку деструктор std::optional автоматично знищить scope_exit, якщо він був створений
}
