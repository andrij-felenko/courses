#include <utility>
#include <type_traits>

template <typename Callback>
class ScopeGuard {
    Callback callback_;
    bool active_{true};

public:
    // Конструктор захоплює довільний функціональний об'єкт
    explicit ScopeGuard(Callback&& cb) noexcept(std::is_nothrow_move_constructible_v<Callback>)
        : callback_(std::move(cb)) {}

    explicit ScopeGuard(const Callback& cb) noexcept(std::is_nothrow_copy_constructible_v<Callback>)
        : callback_(cb) {}

    // Заборона копіювання: відповідальність за відкат належить одному екземпляру
    ScopeGuard(const ScopeGuard&) = delete;
    ScopeGuard& operator=(const ScopeGuard&) = delete;

    // Переміщення передає обов'язок відкату новому об'єкту, знеструмлюючи джерело
    ScopeGuard(ScopeGuard&& other) noexcept(std::is_nothrow_move_constructible_v<Callback>)
        : callback_(std::move(other.callback_)),
          active_(std::exchange(other.active_, false)) {}

    ScopeGuard& operator=(ScopeGuard&& other) noexcept {
        if (this != &other) {
            if (active_) {
                callback_();
            }
            callback_ = std::move(other.callback_);
            active_ = std::exchange(other.active_, false);
        }
        return *this;
    }

    // Деструктор викликає дію відкату, якщо охоронець не був скасований
    ~ScopeGuard() {
        if (active_) {
            callback_();
        }
    }

    // Скасування відкату після успішного завершення операції
    void dismiss() noexcept {
        active_ = false;
    }
};

// Фабрична функція для автоматичного виведення типів аргументів
template <typename Callback>
[[nodiscard]] auto make_scope_guard(Callback&& cb) {
    return ScopeGuard<std::decay_t<Callback>>(std::forward<Callback>(cb));
}
