#include <iostream>
#include <cmath>
#include <compare>
#include <set>
#include <limits>

// Базова геометрична точка: природний частковий порядок
struct Point3D {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    // Автоматично виводить std::partial_ordering через double
    constexpr auto operator<=>(const Point3D&) const = default;
};

// Адаптер тотального порядку для безпечного використання в контейнерах і сортуванні
struct TotalOrderPoint3D {
    Point3D pt;

    // Явне використання стандартного CPO std::strong_order
    std::strong_ordering operator<=>(const TotalOrderPoint3D& other) const noexcept {
        if (auto cmp = std::strong_order(pt.x, other.pt.x); cmp != 0) {
            return cmp;
        }
        if (auto cmp = std::strong_order(pt.y, other.pt.y); cmp != 0) {
            return cmp;
        }
        return std::strong_order(pt.z, other.pt.z);
    }

    bool operator==(const TotalOrderPoint3D& other) const noexcept {
        return (*this <=> other) == 0;
    }
};
