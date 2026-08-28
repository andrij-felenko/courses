inline constexpr double EQUATOR = 40075016.685578488;   // 2π·6378137 м

// Метрів землі в одному пікселі екрана на цій широті й цьому рівні.
double resolution(double lat_deg, int z) {
    return EQUATOR * std::cos(lat_deg * PI / 180.0) / (TILE * pow2(z));
}

struct ScaleBar { double metres, pixels; std::string label; };

// Найбільша «кругла» відстань (ряд 1-2-5), що вміщується в max_px пікселів.
ScaleBar scale_bar(double lat_deg, int z, double max_px = 120.0) {
    const double m_per_px = resolution(lat_deg, z);
    const double raw      = m_per_px * max_px;
    const double p        = std::pow(10.0, std::floor(std::log10(raw)));

    double nice = p;
    for (double c : { 5.0, 2.0, 1.0 })
        if (raw >= c * p) { nice = c * p; break; }

    const std::string label =
        nice >= 1000.0 ? std::to_string(static_cast<long long>(nice / 1000.0)) + " км"
                       : std::to_string(static_cast<long long>(nice)) + " м";
    return { nice, nice / m_per_px, label };
}
