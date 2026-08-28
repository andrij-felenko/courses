namespace std {

// ── 1. std::scope_exit ───────────────────────────────────────────────────────
template <class EF>
class scope_exit {
public:
    // Тип збереженого функціонального об'єкта
    using exit_function = EF;

    // Конструктори
    template <class E>
    explicit scope_exit(E&& fn) noexcept(
        std::is_nothrow_constructible_v<EF, E> ||
        std::is_nothrow_constructible_v<EF, E&>
    );

    scope_exit(scope_exit&& rhs) noexcept(
        std::is_nothrow_move_constructible_v<EF> ||
        std::is_nothrow_copy_constructible_v<EF>
    );

    // Заборона копіювання
    scope_exit(const scope_exit&) = delete;
    scope_exit& operator=(const scope_exit&) = delete;
    scope_exit& operator=(scope_exit&&) = delete;

    // Деструктор
    ~scope_exit() noexcept;

    // Скасування виконання
    void release() noexcept;
};

// Deduction Guide (автоматичне виведення типів аргументів шаблону C++17)
template <class EF>
scope_exit(EF) -> scope_exit<EF>;


// ── 2. std::scope_fail ───────────────────────────────────────────────────────
template <class EF>
class scope_fail {
public:
    using exit_function = EF;

    template <class E>
    explicit scope_fail(E&& fn) noexcept(
        std::is_nothrow_constructible_v<EF, E> ||
        std::is_nothrow_constructible_v<EF, E&>
    );

    scope_fail(scope_fail&& rhs) noexcept(
        std::is_nothrow_move_constructible_v<EF> ||
        std::is_nothrow_copy_constructible_v<EF>
    );

    scope_fail(const scope_fail&) = delete;
    scope_fail& operator=(const scope_fail&) = delete;
    scope_fail& operator=(scope_fail&&) = delete;

    ~scope_fail() noexcept;

    void release() noexcept;
};

template <class EF>
scope_fail(EF) -> scope_fail<EF>;


// ── 3. std::scope_success ────────────────────────────────────────────────────
template <class EF>
class scope_success {
public:
    using exit_function = EF;

    template <class E>
    explicit scope_success(E&& fn) noexcept(
        std::is_nothrow_constructible_v<EF, E> ||
        std::is_nothrow_constructible_v<EF, E&>
    );

    scope_success(scope_success&& rhs) noexcept(
        std::is_nothrow_move_constructible_v<EF> ||
        std::is_nothrow_copy_constructible_v<EF>
    );

    scope_success(const scope_success&) = delete;
    scope_success& operator=(const scope_success&) = delete;
    scope_success& operator=(scope_success&&) = delete;

    ~scope_success() noexcept(noexcept(std::declval<EF&>()()));

    void release() noexcept;
};

template <class EF>
scope_success(EF) -> scope_success<EF>;

} // namespace std
