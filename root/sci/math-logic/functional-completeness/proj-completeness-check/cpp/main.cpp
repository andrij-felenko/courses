#include <bit>          // std::bit_width, std::popcount  (C++20)
#include <cstdint>
#include <iostream>
#include <vector>

using Table = std::vector<uint8_t>;              // table[x] — значення на наборі x

enum : uint8_t { T0 = 1, T1 = 2, M = 4, S = 8, L = 16 };
constexpr uint8_t ALL = T0 | T1 | M | S | L;     // 0b11111 = 31
static const char* WALL[5] = {"зберігає 0", "зберігає 1", "монотонна",
                              "самодвоїста", "лінійна"};

// Поліном Жегалкіна — перетворення Мебіуса на місці, O(n·2ⁿ)
Table zhegalkin(Table a) {
    for (size_t step = 1; step < a.size(); step *= 2)
        for (size_t base = 0; base < a.size(); base += 2 * step)
            for (size_t j = base; j < base + step; ++j)
                a[j + step] ^= a[j];
    return a;
}

bool monotone(const Table& t) {
    const int n = std::bit_width(t.size() - 1);
    for (size_t x = 0; x < t.size(); ++x)
        for (int k = 0; k < n; ++k)
            if (!((x >> k) & 1) && t[x] > t[x | (size_t{1} << k)])
                return false;                    // знайшли ребро, що веде вниз
    return true;
}

bool self_dual(const Table& t) {
    const size_t last = t.size() - 1;
    for (size_t x = 0; x <= last; ++x)
        if (t[x] == t[last ^ x]) return false;   // дзеркало збіглося
    return true;
}

bool linear(const Table& t) {
    const Table p = zhegalkin(t);
    for (size_t mono = 0; mono < p.size(); ++mono)
        if (p[mono] && std::popcount(mono) >= 2) return false;
    return true;
}

// П'ятибітова маска втечі: які стіни пробиває ЦЯ функція
uint8_t escapes(const Table& t) {
    uint8_t m = 0;
    if (t.front() != 0) m |= T0;
    if (t.back() != 1)  m |= T1;
    if (!monotone(t))   m |= M;
    if (!self_dual(t))  m |= S;
    if (!linear(t))     m |= L;
    return m;
}

void report(const char* name, const std::vector<Table>& fs) {
    uint8_t got = 0;
    for (const Table& t : fs) got |= escapes(t);
    std::cout << name;
    if (got == ALL) { std::cout << "  ПОВНИЙ\n"; return; }
    std::cout << "  не повний — ніхто не пробив:";
    for (int i = 0; i < 5; ++i)
        if (!(got & (1 << i))) std::cout << ' ' << WALL[i];
    std::cout << '\n';
}

// Перебір УСІХ 2^(2ⁿ) функцій від n входів — ось тут швидкість уже не забаганка
uint64_t count_solo(int n) {
    const size_t N = size_t{1} << n;
    uint64_t cnt = 0;
    Table t(N);
    for (uint64_t code = 0; code < (uint64_t{1} << N); ++code) {
        for (size_t x = 0; x < N; ++x) t[x] = uint8_t((code >> x) & 1);
        if (escapes(t) == ALL) ++cnt;
    }
    return cnt;
}

int main() {
    const Table NOT_{1, 0}, ZERO{0, 0}, ONE{1, 1};
    const Table AND_{0, 0, 0, 1}, OR_{0, 1, 1, 1}, XOR_{0, 1, 1, 0};
    const Table IMPL{1, 0, 1, 1}, NAND{1, 1, 1, 0};
    const Table MAJ{0, 0, 0, 1, 0, 1, 1, 1};

    report("{NAND}    ", {NAND});
    report("{¬, ∧}    ", {NOT_, AND_});
    report("{∧, ∨}    ", {AND_, OR_});
    report("{⊕, ¬, 1} ", {XOR_, NOT_, ONE});
    report("{→}       ", {IMPL});
    report("{→, 0}    ", {IMPL, ZERO});
    report("{¬, MAJ}  ", {NOT_, MAJ});

    for (int n = 2; n <= 4; ++n)
        std::cout << "n=" << n << ": самодостатніх " << count_solo(n)
                  << " з " << (uint64_t{1} << (size_t{1} << n)) << '\n';
}
