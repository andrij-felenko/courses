template <typename Invocable>
class ScopeGuard {
    Invocable action_;
    bool active_{true};

public:
    // Конструктор захоплює довільну дію за семантикою переміщення
    explicit ScopeGuard(Invocable action) noexcept
        : action_(std::move(action)) {}

    // Деструктор викликає збережену дію, якщо охоронець не скасовано
    ~ScopeGuard() noexcept {
        if (active_) {
            action_();
        }
    }

    // Скасування виконання відкату після успіху
    void dismiss() noexcept {
        active_ = false;
    }

    // Заборона копіювання: відкат не можна дублювати
    ScopeGuard(const ScopeGuard&) = delete;
    ScopeGuard& operator=(const ScopeGuard&) = delete;

    // Переміщення передає обов'язок відкату новому об'єкту, знеструмлюючи джерело
    ScopeGuard(ScopeGuard&& other) noexcept
        : action_(std::move(other.action_)),
          active_(std::exchange(other.active_, false)) {}

    ScopeGuard& operator=(ScopeGuard&& other) = delete;
};
