#include <algorithm>
#include <cmath>
#include <cstdint>
#include <string>
#include <unordered_map>
#include <vector>

// Один запис робочого журналу. Мітка truth дописується пізніше за рішення —
// коли випадок нарешті перевірили.
struct Event {
    std::string slice;   // ключ зрізу: "cam=C|hour=night"
    bool        alarm;   // модель підняла тривогу (оцінка ≥ поріг)
    bool        truth;   // подія справді була
};

// Уся пам'ять, яку коштує зріз: чотири лічильники.
struct Cell {
    std::uint64_t tp = 0, fp = 0, fn = 0, tn = 0;
    std::uint64_t with_event()    const { return tp + fn; }  // випадків, де подія БУЛА
    std::uint64_t without_event() const { return fp + tn; }  // де її НЕ було
};

// Прохід перший: розкласти журнал по зрізах. O(n) часу, O(k) пам'яті.
void accumulate(const std::vector<Event>& log,
                std::unordered_map<std::string, Cell>& by_slice) {
    for (const Event& e : log) {
        Cell& c = by_slice[e.slice];
        if (e.truth) { if (e.alarm) ++c.tp; else ++c.fn; }
        else         { if (e.alarm) ++c.fp; else ++c.tn; }
    }
}

struct Interval { double lo, hi; };

// Квантиль нормалі: таке z, що P(Z > z) = tail. Бісекція по erfc, яка спадає
// монотонно, тож шістдесяти кроків вистачає з великим запасом.
double z_for_tail(double tail) {
    double lo = 0.0, hi = 12.0;
    for (int i = 0; i < 64; ++i) {
        const double mid = 0.5 * (lo + hi);
        if (0.5 * std::erfc(mid / std::sqrt(2.0)) > tail) lo = mid;
        else                                              hi = mid;
    }
    return 0.5 * (lo + hi);
}

// Інтервал Вілсона для частки k/n: не вилазить за [0,1] і не схлопується,
// коли k = 0. Саме він робить малий зріз чесно широким.
Interval wilson(std::uint64_t k, std::uint64_t n, double z) {
    if (n == 0) return { 0.0, 1.0 };
    const double nn   = static_cast<double>(n);
    const double p    = static_cast<double>(k) / nn;
    const double z2   = z * z;
    const double den  = 1.0 + z2 / nn;
    const double mid  = (p + z2 / (2.0 * nn)) / den;
    const double half = z * std::sqrt(p * (1.0 - p) / nn + z2 / (4.0 * nn * nn)) / den;
    return { std::max(0.0, mid - half), std::min(1.0, mid + half) };
}

struct Row {
    std::string   slice;
    std::uint64_t n_without, n_with;
    double        far, far_lo, far_hi;   // хибні тривоги серед випадків без події
    double        mis, mis_lo, mis_hi;   // пропуски серед випадків із подією
};

// Прохід другий: лічильники у звіт. O(k log k) — уся вартість у впорядкуванні.
std::vector<Row> report(const std::unordered_map<std::string, Cell>& by_slice,
                        std::uint64_t min_n, double alpha) {
    // Скільки зрізів переглядаємо — стільки разів і маємо шанс випадково
    // «знайти» найгірший. Рівень ділимо саме на це число.
    std::size_t k = 0;
    for (const auto& kv : by_slice)
        if (kv.second.without_event() >= min_n || kv.second.with_event() >= min_n) ++k;
    if (k == 0) return {};
    const double z = z_for_tail(alpha / (2.0 * static_cast<double>(k)));

    std::vector<Row> out;
    out.reserve(k);
    for (const auto& kv : by_slice) {
        const Cell& c = kv.second;
        const std::uint64_t nw = c.without_event(), np = c.with_event();
        if (nw < min_n && np < min_n) continue;          // замалий — не звітуємо взагалі

        const Interval fi = wilson(c.fp, nw, z);
        const Interval mi = wilson(c.fn, np, z);
        out.push_back(Row{ kv.first, nw, np,
                           nw ? static_cast<double>(c.fp) / nw : 0.0, fi.lo, fi.hi,
                           np ? static_cast<double>(c.fn) / np : 0.0, mi.lo, mi.hi });
    }
    // Упорядковуємо за НИЖНЬОЮ межею, а не за самою часткою: угорі має бути
    // зріз, гірший доведено, а не той, що гірший на вигляд.
    std::sort(out.begin(), out.end(),
              [](const Row& a, const Row& b) { return a.far_lo > b.far_lo; });
    return out;
}
