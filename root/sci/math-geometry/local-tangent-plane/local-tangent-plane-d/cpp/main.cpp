#include <cmath>
#include <numbers>

// Радіус Землі (середній сферичний). Точна реалізація бере широто-залежний
// радіус кривини сфероїда WGS84; для дрона різниця тоне в шумі GPS.
constexpr double EARTH_R = 6371000.0;                    // м
constexpr double DEG2RAD = std::numbers::pi / 180.0;

struct Geo { double lat, lon; };    // градуси
struct NE  { double north, east; }; // метри від точки-початку

// Перехід lat/lon -> місцеві метри «північ, схід» відносно origin.
NE latlon_to_ne(Geo origin, Geo p) {
    double dlat = (p.lat - origin.lat) * DEG2RAD;        // приріст широти в радіанах
    double dlon = (p.lon - origin.lon) * DEG2RAD;        // приріст довготи в радіанах
    return {
        EARTH_R * dlat,                                  // меридіан однаковий скрізь
        EARTH_R * dlon * std::cos(origin.lat * DEG2RAD), // косинус — у origin
    };
}

// Приклад: маршрутна точка на 0.001 градуса північніше й східніше,
// origin на широті Києва (~50.45).
void demo() {
    Geo origin = { 50.4501, 30.5234 };
    Geo wp     = { 50.4511, 30.5244 };   // +0.001° по кожній осі
    NE  d = latlon_to_ne(origin, wp);
    // d.north ≈ 111.2 м  (0.001° широти)
    // d.east  ≈  71.0 м  (0.001° довготи · cos 50.45°)
}
