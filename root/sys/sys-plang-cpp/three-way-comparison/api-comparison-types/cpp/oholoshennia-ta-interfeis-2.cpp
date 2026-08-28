class weak_ordering {
    signed char value;
    constexpr explicit weak_ordering(signed char v) noexcept : value(v) {}

public:
    static const weak_ordering less;
    static const weak_ordering equivalent;
    static const weak_ordering greater;

    // Неявне приведення до часткового порядку
    constexpr operator partial_ordering() const noexcept;

    // Порівняння з числовим нулем
    friend constexpr bool operator==(weak_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator!=(weak_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator< (weak_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator<=(weak_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator> (weak_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator>=(weak_ordering v, /*unspecified-literal-zero*/) noexcept;

    friend constexpr bool operator==(/*unspecified-literal-zero*/, weak_ordering v) noexcept;
    friend constexpr bool operator!=(/*unspecified-literal-zero*/, weak_ordering v) noexcept;
    friend constexpr bool operator< (/*unspecified-literal-zero*/, weak_ordering v) noexcept;
    friend constexpr bool operator<=(/*unspecified-literal-zero*/, weak_ordering v) noexcept;
    friend constexpr bool operator> (/*unspecified-literal-zero*/, weak_ordering v) noexcept;
    friend constexpr bool operator>=(/*unspecified-literal-zero*/, weak_ordering v) noexcept;

    friend constexpr weak_ordering operator<=>(weak_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr weak_ordering operator<=>(/*unspecified-literal-zero*/, weak_ordering v) noexcept;
};
