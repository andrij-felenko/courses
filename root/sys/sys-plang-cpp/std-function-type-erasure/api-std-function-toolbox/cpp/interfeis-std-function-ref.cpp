namespace std {
    template <typename Res, typename... ArgTypes>
    class function_ref<Res(ArgTypes...) /* cv noexcept */> {
    public:
        // Конструктори від будь-якого callable без алокацій
        template <typename F>
        constexpr function_ref(F* f) noexcept;

        template <typename F>
        constexpr function_ref(F&& f) noexcept;

        // Конструктор від методів класів (Bound member pointers)
        template <auto f, typename T>
        constexpr function_ref(T&& obj) noexcept;

        template <auto f>
        constexpr function_ref() noexcept;

        // Конструктори та оператори копіювання (trivially copyable)
        constexpr function_ref(const function_ref&) noexcept = default;
        constexpr function_ref& operator=(const function_ref&) noexcept = default;

        // Оператор виклику
        Res operator()(ArgTypes... args) const /* noexcept */;
    };

    // Автоматична вивід типів (Deduction Guides)
    template <typename F>
    function_ref(F*) -> function_ref<F>;
}
