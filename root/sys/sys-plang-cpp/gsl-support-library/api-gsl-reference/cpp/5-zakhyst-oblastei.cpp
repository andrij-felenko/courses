namespace gsl {
    template <class F>
    class final_action {
    public:
        static_assert(!std::is_reference<F>::value && !std::is_const<F>::value,
                      "F should be a non-const, non-reference callable object");

        explicit final_action(F f) noexcept : clean_action_(std::move(f)), active_(true) {}
        ~final_action() noexcept {
            if (active_) clean_action_();
        }

        // Переміщення дозволено, копіювання суворо заборонено
        final_action(final_action&& other) noexcept;
        final_action(const final_action&) = delete;
        final_action& operator=(const final_action&) = delete;
        final_action& operator=(final_action&&) = delete;

        // Деактивація дії (наприклад, при успішному завершенні транзакції)
        void dismiss() noexcept { active_ = false; }

    private:
        F clean_action_;
        bool active_;
    };

    template <class F>
    [[nodiscard]] final_action<std::decay_t<F>> finally(F&& f) noexcept;
}
