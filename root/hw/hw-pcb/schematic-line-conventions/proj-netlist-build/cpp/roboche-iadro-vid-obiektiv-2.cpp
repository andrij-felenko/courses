// Чи лежить точка p на ВІДРІЗКУ дроту w (включно з кінцями)?
// Дроти на схемі ортогональні, тож достатньо розглянути H- і V-випадки.
static bool point_on_wire(const Point& p, const Wire& w) {
    if (w.a.y == w.b.y) {                                  // горизонтальний
        if (p.y != w.a.y) return false;
        return p.x >= std::min(w.a.x, w.b.x) && p.x <= std::max(w.a.x, w.b.x);
    }
    if (w.a.x == w.b.x) {                                  // вертикальний
        if (p.x != w.a.x) return false;
        return p.y >= std::min(w.a.y, w.b.y) && p.y <= std::max(w.a.y, w.b.y);
    }
    // навскісний дріт — рідкість; повна перевірка колінеарності + меж:
    int64_t cross = int64_t(p.x - w.a.x) * (w.b.y - w.a.y)
                  - int64_t(p.y - w.a.y) * (w.b.x - w.a.x);
    if (cross != 0) return false;
    return p.x >= std::min(w.a.x, w.b.x) && p.x <= std::max(w.a.x, w.b.x)
        && p.y >= std::min(w.a.y, w.b.y) && p.y <= std::max(w.a.y, w.b.y);
}
