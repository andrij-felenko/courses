namespace gsl {
    template <class T>
    class not_null {
    public:
        static_assert(detail::is_pointer_like<T>::value, "T must be a pointer-like type");

        using element_type = typename std::pointer_traits<T>::element_type;

        // Конструктори від валідного покажчика
        constexpr not_null(T u);
        template <class U, class = std::enable_if_t<std::is_convertible<U, T>::value>>
        constexpr not_null(const not_null<U>& other);

        // Заборонені конструктори та оператори присвоєння від nullptr
        constexpr not_null(std::nullptr_t) = delete;
        constexpr not_null& operator=(std::nullptr_t) = delete;

        // Доступ до даних та розіменування
        constexpr element_type& operator*() const noexcept(noexcept(*std::declval<T>()));
        constexpr T operator->() const noexcept;
        constexpr T get() const noexcept;

        // Неявне приведення до базового типу вказівника
        constexpr operator T() const noexcept;

        // Заборона адресної арифметики для запобігання виходу за межі пам'яті (Rule Bounds.1)
        not_null& operator++() = delete;
        not_null& operator--() = delete;
        not_null operator++(int) = delete;
        not_null operator--(int) = delete;
        not_null& operator+=(std::ptrdiff_t) = delete;
        not_null& operator-=(std::ptrdiff_t) = delete;
        void operator[](std::ptrdiff_t) const = delete;
    };

    // Фабрична функція дедукції типу
    template <class T>
    constexpr not_null<T> make_not_null(T&& t);
}
