struct ProfileSpan {
    double s0, s1;      // від і до, метри від початку маршруту (по великому колу)
    double lo, hi;      // ТОЧНІ межі висоти рельєфу на цій ділянці, м AMSL
    bool   known;       // false — у комірці прогалина: відповіді немає взагалі
};

inline double gxOf(double lon) { return (lon + 180.0) * SPD; }
inline double gyOf(double lat) { return (90.0  - lat) * SPD; }

std::vector<ProfileSpan> buildProfile(HgtLibrary& lib, const std::vector<Geo>& route) {
    std::vector<ProfileSpan> out;
    double travelled = 0.0;

    for (size_t v = 0; v + 1 < route.size(); ++v) {
        const Vec3 va = toVec(route[v]), vb = toVec(route[v + 1]);
        const double ang = centralAngle(va, vb), edge = ang * kR;
        const int parts = std::max(1, int(std::ceil(edge / kMaxLeg)));

        for (int q = 0; q < parts; ++q) {
            const Geo a = slerp(va, vb, ang, double(q)     / parts);
            const Geo b = slerp(va, vb, ang, double(q + 1) / parts);
            const double legLen = edge / parts;

            double x0 = gxOf(a.lon), y0 = gyOf(a.lat);
            double x1 = gxOf(b.lon), y1 = gyOf(b.lat);
            // 180-й меридіан: іти коротшим боком, а не через увесь світ.
            if (x1 - x0 >  GW / 2.0) x1 -= GW;
            if (x1 - x0 < -GW / 2.0) x1 += GW;

            const double dx = x1 - x0, dy = y1 - y0, base = travelled;
            walkSegment(x0, y0, x1, y1, [&](const CellHit& h) {
                ProfileSpan s{ base + legLen * h.t0, base + legLen * h.t1, 0.0, 0.0, false };
                Cell c;
                if (readCell(lib, h.gi, h.gj, c)) {
                    // Локальні координати входу в комірку — і локальний приріст.
                    // Різниця (x₀ + dx·t − gi) віднімає два числа порядку 7·10⁵
                    // з відповіддю порядку одиниці. У double похибка лишається
                    // близько 10⁻¹⁰; у float сусідні представні значення там
                    // стоять через 1/16, і комірка перетворилася б на сходинки.
                    // Тому сіткова геометрія тут ЛИШЕ в double, а всередині
                    // комірки параметр уже свій і малий: τ ∈ [0, 1].
                    const double u0 = std::min(1.0, std::max(0.0, x0 + dx * h.t0 - double(h.gi)));
                    const double v0 = std::min(1.0, std::max(0.0, y0 + dy * h.t0 - double(h.gj)));
                    const double du = dx * (h.t1 - h.t0), dv = dy * (h.t1 - h.t0);
                    const Range r = cellRange(c, u0, v0, du, dv);
                    s.lo = r.lo; s.hi = r.hi; s.known = true;
                }
                out.push_back(s);
            });
            travelled += legLen;
        }
    }
    return out;
}
