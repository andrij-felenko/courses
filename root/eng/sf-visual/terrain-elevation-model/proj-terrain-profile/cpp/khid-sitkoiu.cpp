struct CellHit {
    int64_t gi, gj;      // адреса комірки в глобальній сітці
    double  t0, t1;      // параметр уздовж відрізка на вході й на виході
};

// Хід Аманатідеса–Ву: від перетину до перетину з лініями сітки.
template <class F>
void walkSegment(double x0, double y0, double x1, double y1, F&& visit) {
    const double dx = x1 - x0, dy = y1 - y0;
    const double INF = std::numeric_limits<double>::infinity();

    // floor, а НЕ приведення до цілого: (int)(-0.5) дає 0, а треба −1.
    // Після поправки на 180-й меридіан координата тут буває від'ємною.
    int64_t i = int64_t(std::floor(x0)), j = int64_t(std::floor(y0));
    const int64_t iEnd = int64_t(std::floor(x1)), jEnd = int64_t(std::floor(y1));

    const int si = dx > 0 ? 1 : (dx < 0 ? -1 : 0);
    const int sj = dy > 0 ? 1 : (dy < 0 ? -1 : 0);

    const double tdx = si ? std::fabs(1.0 / dx) : INF;   // приріст t на одну комірку
    const double tdy = sj ? std::fabs(1.0 / dy) : INF;
    double tmx = si > 0 ? (double(i) + 1.0 - x0) / dx
               : si < 0 ? (double(i)       - x0) / dx : INF;   // t до найближчої вертикалі
    double tmy = sj > 0 ? (double(j) + 1.0 - y0) / dy
               : sj < 0 ? (double(j)       - y0) / dy : INF;   // t до найближчої горизонталі

    // Кількість кроків відома НАПЕРЕД. Це і межа циклу, і захист від того,
    // що накопичена похибка порівнянь t не дасть ходові дійти до кінця.
    const int64_t steps = (iEnd > i ? iEnd - i : i - iEnd) + (jEnd > j ? jEnd - j : j - jEnd);

    double t = 0.0;
    for (int64_t k = 0; k <= steps; ++k) {
        const double tNext = (k == steps) ? 1.0 : std::min(std::min(tmx, tmy), 1.0);
        visit(CellHit{ i, j, t, tNext });
        if (tNext >= 1.0) return;
        t = tNext;
        if (tmx < tmy) { i += si; tmx += tdx; }   // крокуємо туди, де перетин ближчий
        else           { j += sj; tmy += tdy; }
    }
}
