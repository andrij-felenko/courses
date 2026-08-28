// Спільний кістяк новотипу над double. Параметр Tag робить кожен
// інстанс ОКРЕМИМ типом, навіть якщо всередині той самий double.
template <class Tag>
class Quantity {
    double v_;
public:
    explicit constexpr Quantity(double v) : v_(v) {}
    constexpr double value() const { return v_; }

    friend constexpr bool operator<(Quantity a, Quantity b) { return a.v_ < b.v_; }
    friend constexpr bool operator==(Quantity a, Quantity b) { return a.v_ == b.v_; }
    friend constexpr Quantity operator+(Quantity a, Quantity b) { return Quantity{a.v_ + b.v_}; }
    friend constexpr Quantity operator-(Quantity a, Quantity b) { return Quantity{a.v_ - b.v_}; }
    friend constexpr Quantity operator*(Quantity a, double k)   { return Quantity{a.v_ * k}; }
    friend constexpr Quantity operator*(double k, Quantity a)   { return Quantity{a.v_ * k}; }
};

// Кожна величина — окремий тег-структура (порожня, лише щоб розрізняти типи):
struct MetersTag; struct SecondsTag; struct LatitudeTag; struct LongitudeTag;

using Meters    = Quantity<MetersTag>;
using Seconds   = Quantity<SecondsTag>;
using Latitude  = Quantity<LatitudeTag>;
using Longitude = Quantity<LongitudeTag>;
