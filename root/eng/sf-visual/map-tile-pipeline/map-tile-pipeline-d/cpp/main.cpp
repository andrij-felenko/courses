// Менший ключ — вищий пріоритет.
struct Key {
    int32_t generation;   // 1) свіже покоління завжди попереду застарілого
    int32_t levelDelta;   // 2) свій рівень раніше за сусідні
    int32_t distance;     // 3) від центра екрана до країв
};

Key priorityOf(const TileId& t, const Viewport& vp, int32_t gen) {
    const int32_t dz = std::abs(t.z - vp.targetZoom);
    const int32_t dx = t.centerX() - vp.centerX();
    const int32_t dy = t.centerY() - vp.centerY();
    return Key{ -gen, dz, dx * dx + dy * dy };   // квадрат відстані — без кореня
}
