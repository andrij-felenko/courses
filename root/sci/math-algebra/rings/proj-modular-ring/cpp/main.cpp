#include <cstdint>
#include <iomanip>
#include <iostream>

// ── Елемент кільця лишків ℤ/n: значення завжди зведене в діапазон 0…n−1 ──
struct Zn {
    int64_t v;   // канонічний лишок
    int64_t n;   // модуль
    Zn(int64_t value, int64_t mod) : n(mod) {
        v = ((value % n) + n) % n;   // «+ n» рятує від'ємні: у C++ (−7) % 12 = −7, а не 5
    }
};

Zn  operator+(Zn a, Zn b) { return Zn(a.v + b.v, a.n); }   // a.v + b.v < 2n — влазить у int64
Zn  operator*(Zn a, Zn b) { return Zn(a.v * b.v, a.n); }   // a.v · b.v < n² — теж (n до ~3·10⁹)
bool operator==(Zn a, Zn b) { return a.v == b.v && a.n == b.n; }
std::ostream& operator<<(std::ostream& os, Zn a) { return os << a.v << " (mod " << a.n << ")"; }

// ── Розширений Евклід: gcd(a, b) + коефіцієнти Безу x, y  (a·x + b·y = gcd) ──
int64_t egcd(int64_t a, int64_t b, int64_t& x, int64_t& y) {
    if (b == 0) { x = 1; y = 0; return a; }
    int64_t x1, y1;
    int64_t g = egcd(b, a % b, x1, y1);
    x = y1;
    y = x1 - (a / b) * y1;
    return g;
}

// ── Обернений за множенням до a у ℤ/n, або −1, якщо його нема ──
int64_t inverse(int64_t a, int64_t n) {
    int64_t x, y;
    int64_t g = egcd(((a % n) + n) % n, n, x, y);
    if (g != 1) return -1;             // gcd ≠ 1 → взаємно не прості → оберненого нема
    return ((x % n) + n) % n;          // коефіцієнт Безу x і є обернений; зводимо в 0…n−1
}

int main() {
    const int64_t N = 12;
    std::cout << "3 * 4 = " << Zn(3, N) * Zn(4, N) << "\n\n";

    std::cout << "  *  |";                                   // шапка таблиці
    for (int b = 0; b < N; ++b) std::cout << std::setw(3) << b;
    std::cout << "\n-----+";
    for (int b = 0; b < N; ++b) std::cout << "---";
    std::cout << "\n";
    for (int a = 0; a < N; ++a) {                            // тіло: a·b для всіх пар
        std::cout << std::setw(3) << a << "  |";
        for (int b = 0; b < N; ++b)
            std::cout << std::setw(3) << (Zn(a, N) * Zn(b, N)).v;
        std::cout << "\n";
    }

    std::cout << "\nодиниці (оборотні): ";                   // скан за оберненістю
    for (int a = 1; a < N; ++a) if (inverse(a, N) != -1) std::cout << std::setw(3) << a;
    std::cout << "\nдільники нуля:      ";
    for (int a = 1; a < N; ++a) if (inverse(a, N) == -1) std::cout << std::setw(3) << a;
    std::cout << "\n";
}
