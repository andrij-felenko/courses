#include <string>
#include <tuple>
#include <iostream>

struct GeoCoordinate {
    double latitude;
    double longitude;
    double altitude_meters;
    std::string location_name;
};

// Реалізація функції get<I> через if constexpr
template<std::size_t Index>
constexpr decltype(auto) get(const GeoCoordinate& coord) {
    if constexpr (Index == 0) {
        return coord.latitude;
    } else if constexpr (Index == 1) {
        return coord.longitude;
    } else if constexpr (Index == 2) {
        return coord.altitude_meters;
    } else if constexpr (Index == 3) {
        return coord.location_name;
    } else {
        static_assert(Index < 4, "Індекс виходить за межі структури GeoCoordinate!");
    }
}

// Спеціалізація метаданих для підтримки structured bindings
namespace std {
    template<> struct tuple_size<GeoCoordinate> : std::integral_constant<std::size_t, 4> {};
    template<> struct tuple_element<0, GeoCoordinate> { using type = double; };
    template<> struct tuple_element<1, GeoCoordinate> { using type = double; };
    template<> struct tuple_element<2, GeoCoordinate> { using type = double; };
    template<> struct tuple_element<3, GeoCoordinate> { using type = std::string; };
}

int main() {
    GeoCoordinate station{50.4501, 30.5234, 179.0, "Kyiv-Center"};

    // Пряме розпакування через structured bindings
    const auto& [lat, lon, alt, name] = station;
    std::cout << "Станція: " << name << " (" << lat << ", " << lon << ")\n";
    return 0;
}
