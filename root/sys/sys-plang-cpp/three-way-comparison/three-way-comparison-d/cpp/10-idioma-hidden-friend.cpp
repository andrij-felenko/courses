class Fraction {
    int num{0};
    int den{1};

public:
    constexpr Fraction(int n, int d) noexcept : num(n), den(d) {}

    // Hidden Friend: функція не засмічує простір імен
    friend constexpr auto operator<=>(const Fraction& a, const Fraction& b) noexcept {
        // Перехресне множення для уникнення ділення з плаваючою комою
        int64_t left  = static_cast<int64_t>(a.num) * b.den;
        int64_t right = static_cast<int64_t>(b.num) * a.den;
        return left <=> right;
    }

    friend constexpr bool operator==(const Fraction& a, const Fraction& b) noexcept {
        return (static_cast<int64_t>(a.num) * b.den) ==
               (static_cast<int64_t>(b.num) * a.den);
    }
};
