// Довгота -> дробова тайлова X. НЕ обрізається: значення може вийти за [0,n).
double lon_to_x(double lon_deg, int z) {
    return (lon_deg + 180.0) / 360.0 * pow2(z);
}

// Широта -> дробова тайлова Y. Зріз до ±MAX_LAT ОБОВ'ЯЗКОВИЙ перед asinh/log.
double lat_to_y(double lat_deg, int z) {
    const double lat = std::clamp(lat_deg, -MAX_LAT, MAX_LAT);
    const double ym  = std::asinh(std::tan(lat * PI / 180.0));   // = ln tan(π/4 + φ/2)
    return (0.5 - ym / (2.0 * PI)) * pow2(z);
}

// Усі тайли рівня z, що накривають прямокутник. Коректно через 180-й меридіан.
std::vector<TileId> tiles_for_bbox(const BBox& b, int z) {
    const std::int64_t n = std::int64_t{1} << z;    // z ≤ 62, інакше UB

    // y: обрізаємо — полюсів на карті немає, склеювати нема чого
    const std::int64_t y_top = std::max<std::int64_t>(
        0, static_cast<std::int64_t>(std::floor(lat_to_y(b.north, z))));
    const std::int64_t y_bot = std::min<std::int64_t>(
        n - 1, static_cast<std::int64_t>(std::floor(lat_to_y(b.south, z))));

    // x: ширину рахуємо в ДРОБОВИХ координатах, до floor
    const double f_left = lon_to_x(b.west, z);
    double f_right      = lon_to_x(b.east, z);
    if (f_right < f_left) f_right += static_cast<double>(n);   // перетнули шов

    const std::int64_t x_left = static_cast<std::int64_t>(std::floor(f_left));
    const std::int64_t span_x = std::min<std::int64_t>(
        n, static_cast<std::int64_t>(std::floor(f_right)) - x_left + 1);

    std::vector<TileId> out;
    if (y_bot < y_top || span_x <= 0) return out;
    out.reserve(static_cast<std::size_t>((y_bot - y_top + 1) * span_x));
    for (std::int64_t y = y_top; y <= y_bot; ++y)
        for (std::int64_t i = 0; i < span_x; ++i)
            out.push_back({ z, ((x_left + i) % n + n) % n, y });   // циклічність по x
    return out;
}
