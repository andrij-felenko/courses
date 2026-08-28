struct Viewport {
    int32_t  zoom = 0;              // цілий рівень, який малюють цього кадру
    double   cx = 0, cy = 0;        // центр екрана в тайлових координатах цього рівня
    double   halfW = 1, halfH = 1;  // піврозміри екрана в тих самих одиницях
    uint32_t variant = 0;
    uint64_t generation = 0;        // росте на КОЖНУ зміну положення чи масштабу
};

// Квадрат нормованої відстані від центра екрана: 1.0 — приблизно край екрана.
// ldexp множить на 2ᵏ точно й без ділень, тому переведення тайла рівня t.z
// в одиниці рівня vp.zoom — це правка порядку числа, а не арифметика.
inline double dist2(const TileId& t, const Viewport& vp) noexcept {
    const int    shift = vp.zoom - t.z;
    const double tx = std::ldexp(t.x + 0.5, shift);
    const double ty = std::ldexp(t.y + 0.5, shift);
    const double dx = (tx - vp.cx) / vp.halfW;
    const double dy = (ty - vp.cy) / vp.halfH;
    return dx * dx + dy * dy;
}

// Цінність для КЕША: більше — цінніше; витісняємо найменш цінне.
inline double cacheValue(const TileId& t, const Viewport& vp) noexcept {
    if (t.variant != vp.variant) return -1e300;   // чужий стиль чи щільність — геть першим
    const int dl = std::abs(vp.zoom - t.z);
    double v = -2.0 * dl - dist2(t, vp);
    if (t.z < vp.zoom) v += 2.0;                  // предки закривають діри — тримаємо
    return v;
}
