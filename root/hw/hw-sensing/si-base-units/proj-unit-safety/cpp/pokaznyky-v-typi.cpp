// Одиниця = три цілих у типі: показники M (маса), L (довжина), T (час).
template <int M, int L, int T>
struct Quantity {
    double value;
    explicit constexpr Quantity(double v) : value(v) {}
};

// Додавати можна ЛИШЕ однакові розмірності — типи мусять збігтися.
template <int M, int L, int T>
constexpr Quantity<M, L, T> operator+(Quantity<M, L, T> a, Quantity<M, L, T> b) {
    return Quantity<M, L, T>{ a.value + b.value };
}

// Множення СКЛАДАЄ показники, ділення — ВІДНІМАЄ: похідна одиниця сама собою.
template <int M1,int L1,int T1, int M2,int L2,int T2>
constexpr Quantity<M1+M2, L1+L2, T1+T2>
operator*(Quantity<M1,L1,T1> a, Quantity<M2,L2,T2> b) {
    return Quantity<M1+M2, L1+L2, T1+T2>{ a.value * b.value };
}
template <int M1,int L1,int T1, int M2,int L2,int T2>
constexpr Quantity<M1-M2, L1-L2, T1-T2>
operator/(Quantity<M1,L1,T1> a, Quantity<M2,L2,T2> b) {
    return Quantity<M1-M2, L1-L2, T1-T2>{ a.value / b.value };
}

using Length   = Quantity<0, 1, 0>;    // м
using Time     = Quantity<0, 0, 1>;    // с
using Mass     = Quantity<1, 0, 0>;    // кг
using Velocity = Quantity<0, 1, -1>;   // м/с
