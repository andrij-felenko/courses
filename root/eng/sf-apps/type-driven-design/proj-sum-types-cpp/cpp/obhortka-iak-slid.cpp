class Latitude {
    double deg_;
public:
    explicit constexpr Latitude(double d) : deg_(d) {}   // лише навмисне загортання
    constexpr double value() const { return deg_; }      // дістати голе число
};

class Longitude {
    double deg_;
public:
    explicit constexpr Longitude(double d) : deg_(d) {}
    constexpr double value() const { return deg_; }
};

void moveTo(Latitude lat, Longitude lon);
