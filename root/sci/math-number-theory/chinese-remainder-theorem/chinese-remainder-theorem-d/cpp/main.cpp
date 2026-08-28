#include <cstdint>
#include <vector>
#include <stdexcept>

// розширений Евклід: НСД(a, b) плюс x, y такі, що a·x + b·y = НСД(a, b)
static int64_t egcd(int64_t a, int64_t b, int64_t &x, int64_t &y) {
    if (b == 0) { x = 1; y = 0; return a; }
    int64_t x1, y1;
    int64_t g = egcd(b, a % b, x1, y1);
    x = y1;
    y = x1 - (a / b) * y1;
    return g;
}

static int64_t inv_mod(int64_t a, int64_t m) {
    int64_t x, y;
    if (egcd(a % m, m, x, y) != 1) throw std::domain_error("модулі не взаємно прості");
    return (x % m + m) % m;          // egcd може дати від'ємний x — нормалізуємо
}

int64_t crt(const std::vector<int64_t> &res, const std::vector<int64_t> &mod) {
    int64_t N = 1;
    for (int64_t n : mod) N *= n;
    __int128 x = 0;                  // добуток a·Nᵢ·Mᵢ переростає int64_t уже на скромних модулях
    for (size_t i = 0; i < mod.size(); ++i) {
        int64_t Ni = N / mod[i];
        int64_t Mi = inv_mod(Ni % mod[i], mod[i]);
        x += (__int128)res[i] * Ni % N * Mi % N;   // зводимо після кожного множення
    }
    return (int64_t)(x % N);
}
