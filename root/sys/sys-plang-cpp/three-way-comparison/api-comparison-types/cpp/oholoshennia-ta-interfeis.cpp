class strong_ordering {
    // Внутрішній стан (зазвичай int8_t: -1 для less, 0 для equal, 1 для greater)
    signed char value;

    // Закритий конструктор для ініціалізації констант
    constexpr explicit strong_ordering(signed char v) noexcept : value(v) {}

public:
    // Статичні константи можливих результатів
    static const strong_ordering less;
    static const strong_ordering equal;
    static const strong_ordering equivalent;
    static const strong_ordering greater;

    // Неявні оператори приведення до слабших категорій
    constexpr operator weak_ordering() const noexcept;
    constexpr operator partial_ordering() const noexcept;

    // Оператори порівняння з числовим нулем
    friend constexpr bool operator==(strong_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator!=(strong_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator< (strong_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator<=(strong_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator> (strong_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator>=(strong_ordering v, /*unspecified-literal-zero*/) noexcept;

    // Перевернуті оператори (0 == v, 0 < v тощо)
    friend constexpr bool operator==(/*unspecified-literal-zero*/, strong_ordering v) noexcept;
    friend constexpr bool operator!=(/*unspecified-literal-zero*/, strong_ordering v) noexcept;
    friend constexpr bool operator< (/*unspecified-literal-zero*/, strong_ordering v) noexcept;
    friend constexpr bool operator<=(/*unspecified-literal-zero*/, strong_ordering v) noexcept;
    friend constexpr bool operator> (/*unspecified-literal-zero*/, strong_ordering v) noexcept;
    friend constexpr bool operator>=(/*unspecified-literal-zero*/, strong_ordering v) noexcept;

    // Тричленне порівняння категорій між собою
    friend constexpr strong_ordering operator<=>(strong_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr strong_ordering operator<=>(/*unspecified-literal-zero*/, strong_ordering v) noexcept;
};
