namespace std {
    template <typename Res, typename... ArgTypes>
    class function<Res(ArgTypes...)> {
    public:
        using result_type = Res;

        // Вкладені typedefs для сумісності з C++11 (видалені у C++20)
        // using argument_type = ArgType;              (лише при 1 аргументі)
        // using first_argument_type = Arg1;           (лише при 2 аргументах)
        // using second_argument_type = Arg2;          (лише при 2 аргументах)

        // Конструктори та деструктор
        constexpr function() noexcept;
        constexpr function(nullptr_t) noexcept;
        function(const function& other);
        function(function&& other) noexcept;

        template <typename F>
        function(F&& f);

        // Історичні конструктори з алокаторами (вилучені у C++17)
        // template <typename Alloc> function(allocator_arg_t, const Alloc&) noexcept;
        // template <typename Alloc, typename F> function(allocator_arg_t, const Alloc&, F&&);

        ~function();

        // Оператори присвоєння
        function& operator=(const function& other);
        function& operator=(function&& other) noexcept;
        function& operator=(nullptr_t) noexcept;

        template <typename F>
        function& operator=(F&& f);

        template <typename F>
        function& operator=(reference_wrapper<F> f) noexcept;

        // Модифікатори
        void swap(function& other) noexcept;

        // Обстерігачі стану (State Observers)
        explicit operator bool() const noexcept;

        // Оператор виклику
        Res operator()(ArgTypes... args) const;

        // Інтроспекція типів (RTTI Target Access)
        const std::type_info& target_type() const noexcept;

        template <typename T>
        T* target() noexcept;

        template <typename T>
        const T* target() const noexcept;
    };

    // Нечленські функції порівняння та swap
    template <typename Res, typename... Args>
    bool operator==(const function<Res(Args...)>& f, nullptr_t) noexcept;

    template <typename Res, typename... Args>
    bool operator==(nullptr_t, const function<Res(Args...)>& f) noexcept;

    template <typename Res, typename... Args>
    bool operator!=(const function<Res(Args...)>& f, nullptr_t) noexcept;

    template <typename Res, typename... Args>
    bool operator!=(nullptr_t, const function<Res(Args...)>& f) noexcept;

    template <typename Res, typename... Args>
    void swap(function<Res(Args...)>& lhs, function<Res(Args...)>& rhs) noexcept;
}
