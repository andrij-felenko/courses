class ScopeFail {
    std::function<void()> action_;
    int uncaught_on_enter_{std::uncaught_exceptions()};

public:
    explicit ScopeFail(std::function<void()> action)
        : action_(std::move(action)) {}

    ~ScopeFail() noexcept {
        // Якщо кількість активних винятків зросла — стався новий виняток!
        if (std::uncaught_exceptions() > uncaught_on_enter_) {
            action_();
        }
    }
};

class ScopeSuccess {
    std::function<void()> action_;
    int uncaught_on_enter_{std::uncaught_exceptions()};

public:
    explicit ScopeSuccess(std::function<void()> action)
        : action_(std::move(action)) {}

    ~ScopeSuccess() noexcept {
        // Якщо кількість винятків не змінилася — вихід був нормальним
        if (std::uncaught_exceptions() <= uncaught_on_enter_) {
            action_();
        }
    }
};
