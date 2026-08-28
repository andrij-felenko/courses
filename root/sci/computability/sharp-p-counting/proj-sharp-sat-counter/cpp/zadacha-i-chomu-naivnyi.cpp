#include <vector>
#include <string>
#include <unordered_map>
#include <algorithm>
#include <cstdint>
#include <cstdio>
using std::vector;

using Lit    = int;                  // v>0 → xᵥ істинна;  v<0 → ¬x|v|
using Clause = vector<Lit>;          // диз'юнкція літералів
using CNF    = vector<Clause>;       // кон'юнкція клауз
using Count  = unsigned long long;   // лічильник моделей (вміщає до 2⁶³)

inline int var(Lit L)       { return L > 0 ? L : -L; }               // номер змінної літерала
inline int bits(uint64_t m) { int k = 0; for (; m; m &= m - 1) ++k; return k; }  // популяція одиниць

// Еталон: прямий перебір усіх 2ⁿ наборів. Лише для звірки на малих n.
Count bruteForce(const CNF& F, int n) {
    Count models = 0;
    for (uint64_t a = 0; a < (1ULL << n); ++a) {       // a — набір: біт (v-1) = значення xᵥ
        bool ok = true;
        for (const Clause& c : F) {
            bool sat = false;
            for (Lit L : c)
                if (((a >> (var(L) - 1)) & 1) == (Count)(L > 0)) { sat = true; break; }
            if (!sat) { ok = false; break; }
        }
        models += ok;
    }
    return models;
}
