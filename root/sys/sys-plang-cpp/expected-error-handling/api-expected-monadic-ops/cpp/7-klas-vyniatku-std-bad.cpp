namespace std {
    template <typename E>
    class bad_expected_access : public bad_expected_access<void> {
    private:
        E val_; // Зберігає копію або переміщений об'єкт помилки
    public:
        explicit bad_expected_access(E e) : val_(std::move(e)) {}

        // Доступ до збереженого об'єкта помилки
        const E& error() const & noexcept { return val_; }
        E& error() & noexcept { return val_; }
        const E&& error() const && noexcept { return std::move(val_); }
        E&& error() && noexcept { return std::move(val_); }

        const char* what() const noexcept override {
            return "bad access to std::expected in error state";
        }
    };

    // Спеціалізація для void
    template <>
    class bad_expected_access<void> : public std::exception {
    public:
        const char* what() const noexcept override {
            return "bad access to std::expected<void>";
        }
    };
}
