namespace std {
    template <typename Res, typename... ArgTypes>
    class move_only_function<Res(ArgTypes...) /* cv ref noexcept */> {
    public:
        using result_type = Res;

        // Конструктори
        constexpr move_only_function() noexcept;
        constexpr move_only_function(nullptr_t) noexcept;
        move_only_function(move_only_function&& other) noexcept;

        template <typename F>
        move_only_function(F&& f);

        template <typename VT, typename... Args>
        explicit move_only_function(in_place_type_t<VT>, Args&&... args);

        template <typename VT, typename U, typename... Args>
        explicit move_only_function(in_place_type_t<VT>, initializer_list<U> il, Args&&... args);

        // ДЕСТРУКТОР ТА ЗМАГАЛЬНІ ОПЕРАТОРИ КОПІЮВАННЯ ВІДСУТНІ (Deleted)
        move_only_function(const move_only_function&) = delete;
        move_only_function& operator=(const move_only_function&) = delete;

        ~move_only_function();

        // Оператори присвоєння
        move_only_function& operator=(move_only_function&& other) noexcept;
        move_only_function& operator=(nullptr_t) noexcept;

        template <typename F>
        move_only_function& operator=(F&& f);

        // Модифікатори
        void swap(move_only_function& other) noexcept;

        // Обстерігачі
        explicit operator bool() const noexcept;

        // Оператор виклику успадковує cv/ref/noexcept кваліфікатори шаблону!
        Res operator()(ArgTypes... args) /* cv ref noexcept */;
    };

    // Нечленські функції порівняння та swap
    template <typename Res, typename... Args>
    bool operator==(const move_only_function<Res(Args...)>& f, nullptr_t) noexcept;

    template <typename Res, typename... Args>
    void swap(move_only_function<Res(Args...)>& lhs, move_only_function<Res(Args...)>& rhs) noexcept;
}
