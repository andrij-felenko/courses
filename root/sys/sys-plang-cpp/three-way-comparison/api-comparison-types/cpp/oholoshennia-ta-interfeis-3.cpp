class partial_ordering {
    // Внутрішній стан (зазвичай: -1 для less, 0 для equivalent, 1 для greater, 2 для unordered)
    signed char value;
    constexpr explicit partial_ordering(signed char v) noexcept : value(v) {}

public:
    static const partial_ordering less;
    static const partial_ordering equivalent;
    static const partial_ordering greater;
    static const partial_ordering unordered;

    // Порівняння з числовим нулем
    friend constexpr bool operator==(partial_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator!=(partial_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator< (partial_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator<=(partial_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator> (partial_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator>=(partial_ordering v, /*unspecified-literal-zero*/) noexcept;

    friend constexpr bool operator==(/*unspecified-literal-zero*/, partial_ordering v) noexcept;
    friend constexpr bool operator!=(/*unspecified-literal-zero*/, partial_ordering v) noexcept;
    friend constexpr bool operator< (/*unspecified-literal-zero*/, partial_ordering v) noexcept;
    friend constexpr bool operator<=(/*unspecified-literal-zero*/, partial_ordering v) noexcept;
    friend constexpr bool operator> (/*unspecified-literal-zero*/, partial_ordering v) noexcept;
    friend constexpr bool operator>=(/*unspecified-literal-zero*/, partial_ordering v) noexcept;

    friend constexpr partial_ordering operator<=>(partial_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr partial_ordering operator<=>(/*unspecified-literal-zero*/, partial_ordering v) noexcept;
};
