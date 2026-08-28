#include <iostream>
#include <string>
#include <tuple>
#include <utility>

// Користувацький клас з приватними полями
class GeoPoint {
private:
    double m_lat;
    double m_lon;
    std::string m_label;

public:
    GeoPoint(double lat, double lon, std::string label)
        : m_lat(lat), m_lon(lon), m_label(std::move(label)) {}

    // Геттери доступу
    double latitude() const { return m_lat; }
    double longitude() const { return m_lon; }
    const std::string& label() const { return m_label; }

    // Шаблонний виклик get<i>() усередині класу або як friend
    template <std::size_t I>
    decltype(auto) get() const {
        if constexpr (I == 0) return m_lat;
        else if constexpr (I == 1) return m_lon;
        else if constexpr (I == 2) return m_label;
    }

    // Мутабельний get<i>() для підтримки розкладання за мінливим посиланням (auto&)
    template <std::size_t I>
    decltype(auto) get() {
        if constexpr (I == 0) return (m_lat);
        else if constexpr (I == 1) return (m_lon);
        else if constexpr (I == 2) return (m_label);
    }
};

// 1. Спеціалізація std::tuple_size
namespace std {
    template <>
    struct tuple_size<GeoPoint> : std::integral_constant<std::size_t, 3> {};

    // 2. Спеціалізація std::tuple_element для кожного індексу
    template <std::size_t I>
    struct tuple_element<I, GeoPoint> {
        using type = std::conditional_t<I == 2, std::string, double>;
    };
}
