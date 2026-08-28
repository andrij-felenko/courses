class Feet {
    double ft_;
public:
    explicit constexpr Feet(double ft) : ft_(ft) {}
    constexpr double value() const { return ft_; }
};

// єдиний легальний міст між одиницями — явне перетворення
constexpr Meters toMeters(Feet f) { return Meters{ f.value() * 0.3048 }; }
constexpr Feet   toFeet(Meters m) { return Feet{   m.value() / 0.3048 }; }
