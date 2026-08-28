// ── 1. Мінімальний запас над рельєфом ──────────────────────────────────────
struct Clearance {
    double minGap    = std::numeric_limits<double>::infinity();
    double atDistance = 0.0;
    bool   complete   = true;     // false — на маршруті є прогалини даних
};

// flightAmsl — саме НАД РІВНЕМ МОРЯ. Висота з навігаційного приймача відлічена
// від еліпсоїда; підставити її сюди — систематично занизити запас на ундуляцію.
Clearance minClearance(const std::vector<ProfileSpan>& p, double flightAmsl) {
    Clearance c;
    for (const ProfileSpan& s : p) {
        if (!s.known) { c.complete = false; continue; }   // ← не нуль і не «мовчки далі»
        const double gap = flightAmsl - s.hi;             // найгірше на ділянці
        if (gap < c.minGap) { c.minGap = gap; c.atDistance = s.s0; }
    }
    return c;
}

// ── 2. Пряма видимість A → B ───────────────────────────────────────────────
// Радіус першої зони Френеля в точці d траси довжиною D, м.
inline double fresnel1(double d, double total, double lambda) {
    return std::sqrt(lambda * d * (total - d) / total);
}

struct Sight {
    bool   clear      = true;   // ЧИТАТИ лише разом із complete: на суцільній
    double atDistance = 0.0;    // прогалині траса «вільна» просто через брак даних
    double margin     = std::numeric_limits<double>::infinity();  // ≤ 0 — перекрито
    bool   complete   = true;
};

Sight lineOfSight(const std::vector<ProfileSpan>& p,
                  double antennaA, double antennaB,   // м AMSL, разом із щоглою
                  double total,                        // повна довжина траси, м
                  double lambda = 0.0,                 // 0 — чиста геометрія, без Френеля
                  double kFactor = 4.0 / 3.0)          // 4/3 — рефракція для радіо
{
    Sight best;
    for (const ProfileSpan& s : p) {
        if (!s.known) { best.complete = false; continue; }
        for (const double d : { s.s0, s.s1 }) {
            // Здуття планети над хордою між кінцями траси піднімає рельєф.
            const double bulge = d * (total - d) / (2.0 * kFactor * kR);
            const double need  = lambda > 0.0 ? 0.6 * fresnel1(d, total, lambda) : 0.0;
            const double sight = antennaA + (antennaB - antennaA) * (d / total);
            const double margin = sight - (s.hi + bulge + need);
            if (margin < best.margin) {
                best.margin = margin;
                best.atDistance = d;
                best.clear = margin > 0.0;
            }
        }
    }
    return best;
}
