#include <cstdint>
#include <vector>
#include <random>
#include <cmath>
#include <numeric>
using Bytes = std::vector<uint8_t>;

std::vector<double> robust_soliton(int k, double c = 0.05, double delta = 0.5) {
    std::vector<double> p(k + 1, 0.0);              // p[1..k]; p[0] не вживають
    p[1] = 1.0 / k;                                 // ідеальний солітон ρ
    for (int d = 2; d <= k; ++d) p[d] = 1.0 / (double(d) * (d - 1));
    double R = c * std::log(k / delta) * std::sqrt(double(k));  // τ і сплеск при ⌊k/R⌋
    int kr = int(k / R);
    for (int d = 1; d < kr; ++d) p[d] += R / (double(d) * k);
    if (kr >= 1) p[kr] += R * std::log(R / delta) / k;
    double beta = std::accumulate(p.begin(), p.end(), 0.0);
    for (double& x : p) x /= beta;                  // нормуємо → μ
    return p;
}

// один double у [0,1) із 64-бітного слова — однаково на обох кінцях
static inline double canon(std::mt19937_64& g) {
    return (g() >> 11) * (1.0 / 9007199254740992.0);
}

// Із самого зерна — степінь і набір індексів. Спільна для кодера й декодера.
std::vector<int> droplet_recipe(uint64_t seed, int k, const std::vector<double>& mu) {
    std::mt19937_64 g(seed);
    double r = canon(g), acc = 0.0;
    int d = k;
    for (int i = 1; i <= k; ++i) {                  // вибір степеня за μ
        acc += mu[i];
        if (r <= acc) { d = i; break; }
    }
    std::vector<int> pool(k);
    std::iota(pool.begin(), pool.end(), 0);
    for (int i = 0; i < d; ++i) {                   // часткове Фішера–Єйтса: d кроків
        int j = i + int(canon(g) * (k - i));
        std::swap(pool[i], pool[j]);
    }
    return {pool.begin(), pool.begin() + d};        // d РІЗНИХ індексів блоків
}

void xor_into(Bytes& dst, const Bytes& src) {       // dst ^= src, побайтово
    for (size_t i = 0; i < dst.size(); ++i) dst[i] ^= src[i];
}

struct LTEncoder {
    const std::vector<Bytes>& blocks;
    int k;
    std::vector<double> mu;
    LTEncoder(const std::vector<Bytes>& b, std::vector<double> m)
        : blocks(b), k(int(b.size())), mu(std::move(m)) {}

    Bytes droplet(uint64_t seed) const {            // на дроті: зерно + вантаж
        Bytes payload(blocks[0].size(), 0);
        for (int i : droplet_recipe(seed, k, mu)) xor_into(payload, blocks[i]);
        return payload;
    }
};
