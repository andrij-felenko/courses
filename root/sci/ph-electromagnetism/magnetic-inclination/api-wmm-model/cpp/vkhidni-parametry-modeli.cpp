/* cpp */
namespace navigation::wmm {

struct WmmInput {
    double latitude_deg{0.0};   // Географічна широта [-90.0 .. +90.0°] (WGS-84)
    double longitude_deg{0.0};  // Географічна довгота [-180.0 .. +180.0°] (WGS-84)
    double altitude_km{0.0};    // Висота над еліпсоїдом WGS-84 у км
    double decimal_year{2026.0};// Час у десяткових роках
};

} // namespace navigation::wmm
