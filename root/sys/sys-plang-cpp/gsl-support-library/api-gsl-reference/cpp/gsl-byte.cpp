namespace gsl {
    enum class byte : unsigned char {};

    constexpr byte operator&(byte l, byte r) noexcept;
    constexpr byte operator|(byte l, byte r) noexcept;
    constexpr byte operator^(byte l, byte r) noexcept;
    constexpr byte operator~(byte b) noexcept;

    template <class IntegerType>
    constexpr byte operator<<(byte b, IntegerType shift) noexcept;
    template <class IntegerType>
    constexpr byte operator>>(byte b, IntegerType shift) noexcept;

    template <class IntegerType>
    constexpr IntegerType to_integer(byte b) noexcept;
}
