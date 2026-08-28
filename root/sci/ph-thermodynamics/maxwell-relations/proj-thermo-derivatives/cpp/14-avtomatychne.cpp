struct Dual {
    double val; // Значення функції f(x)
    double der; // Значення похідної f'(x)

    constexpr Dual operator+(Dual o) const noexcept {
        return Dual{val + o.val, der + o.der};
    }
    constexpr Dual operator*(Dual o) const noexcept {
        return Dual{val * o.val, val * o.der + der * o.val}; // Правило Лейбніца
    }
};

Dual pressure_dual(Dual T, Dual V, double R, double a, double b) {
    Dual term1 = Dual{R, 0.0} * T * Dual{1.0 / (V.val - b), -V.der / ((V.val - b)*(V.val - b))};
    Dual term2 = Dual{a / (V.val * V.val), -2.0 * a * V.der / (V.val * V.val * V.val)};
    return term1 + Dual{-term2.val, -term2.der};
}
