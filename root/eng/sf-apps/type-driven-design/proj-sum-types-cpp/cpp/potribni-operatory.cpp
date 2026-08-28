class Meters {
    double m_;
public:
    explicit constexpr Meters(double m) : m_(m) {}
    constexpr double value() const { return m_; }

    // порівняння: метр із метром — коректно
    friend constexpr bool operator<(Meters a, Meters b) { return a.m_ < b.m_; }
    friend constexpr bool operator==(Meters a, Meters b) { return a.m_ == b.m_; }

    // додавання/віднімання: метр + метр = метр (розмірність зберігається)
    friend constexpr Meters operator+(Meters a, Meters b) { return Meters{a.m_ + b.m_}; }
    friend constexpr Meters operator-(Meters a, Meters b) { return Meters{a.m_ - b.m_}; }

    // множення на безрозмірне число: 3 · метр = метр (масштаб)
    friend constexpr Meters operator*(Meters a, double k) { return Meters{a.m_ * k}; }
    friend constexpr Meters operator*(double k, Meters a) { return Meters{a.m_ * k}; }
};
