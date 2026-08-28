struct Cell { double h00, h10, h01, h11; };   // 00 — вузол (gi, gj); 10 — схід; 01 — південь

// false, якщо ХОЧ ОДИН кут є прогалиною: інтерполювати прогалину не можна.
inline bool readCell(HgtLibrary& lib, int64_t gi, int64_t gj, Cell& c) {
    int16_t a, b, d, e;
    if (!lib.node(gi,     gj    , a) || !lib.node(gi + 1, gj    , b) ||
        !lib.node(gi,     gj + 1, d) || !lib.node(gi + 1, gj + 1, e)) return false;
    c = Cell{ double(a), double(b), double(d), double(e) };
    return true;
}

struct Range { double lo, hi; };

// Найменше й найбільше значення білінійної поверхні комірки на відрізку
// (u₀, v₀) → (u₀+du, v₀+dv), параметр τ ∈ [0, 1].
//
//   h(u, v) = h₀₀ + c₁·u + c₂·v + c₃·u·v
//   u = u₀ + du·τ ,  v = v₀ + dv·τ
//   ⟹ h(τ) = A·τ² + B·τ + C
//     A = c₃·du·dv
//     B = c₁·du + c₂·dv + c₃·(u₀·dv + du·v₀)
//     C = h₀₀ + c₁·u₀ + c₂·v₀ + c₃·u₀·v₀
inline Range cellRange(const Cell& c, double u0, double v0, double du, double dv) {
    const double c1 = c.h10 - c.h00;
    const double c2 = c.h01 - c.h00;
    const double c3 = c.h00 - c.h10 - c.h01 + c.h11;   // «перекіс» комірки

    const double A = c3 * du * dv;
    const double B = c1 * du + c2 * dv + c3 * (u0 * dv + du * v0);
    const double C = c.h00 + c1 * u0 + c2 * v0 + c3 * u0 * v0;

    const double h0 = C, h1 = A + B + C;
    Range r{ std::min(h0, h1), std::max(h0, h1) };

    // A == 0 — відрізок паралельний осі сітки: висота вздовж нього ЛІНІЙНА,
    // і кінці вже дали остаточну відповідь.
    if (A != 0.0) {
        const double tv = -B / (2.0 * A);
        if (tv > 0.0 && tv < 1.0) {
            const double hv = (A * tv + B) * tv + C;
            if (A < 0.0) r.hi = std::max(r.hi, hv);   // вітки вниз — усередині максимум
            else         r.lo = std::min(r.lo, hv);   // вітки вгору — усередині мінімум
        }
    }
    return r;
}
