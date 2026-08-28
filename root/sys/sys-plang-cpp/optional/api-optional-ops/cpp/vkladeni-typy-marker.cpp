namespace std {
    // Основний шаблон класу
    template <class T>
    class optional;

    // Маркер порожнього стану
    struct nullopt_t {
        explicit constexpr nullopt_t(int) {}
    };
    inline constexpr nullopt_t nullopt{0};

    // Виняток при некоректному доступі
    class bad_optional_access : public std::exception {
    public:
        bad_optional_access() noexcept;
        virtual const char* what() const noexcept override;
    };
}
