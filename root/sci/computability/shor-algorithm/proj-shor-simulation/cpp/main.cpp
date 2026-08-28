#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numeric>
#include <random>
#include <numbers>
#include <optional>
#include <span>

using Complex = std::complex<double>;

// Швидке модульне піднесення до степеня (a^exp mod n)
uint64_t mod_exp(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) res = (__uint128_t(res) * base) % mod;
        base = (__uint128_t(base) * base) % mod;
        exp >>= 1;
    }
    return res;
}

// Обернене квантове перетворення Фур'є над вектором квантового стану
void apply_inverse_qft(std::span<Complex> state) {
    const size_t q = state.size();
    std::vector<Complex> out(q, Complex(0.0, 0.0));
    const double inv_sqrt_q = 1.0 / std::sqrt(static_cast<double>(q));
    const double two_pi = 2.0 * std::numbers::pi;

    for (size_t y = 0; y < q; ++y) {
        Complex sum(0.0, 0.0);
        for (size_t x = 0; x < q; ++x) {
            double angle = -two_pi * static_cast<double>(x * y) / static_cast<double>(q);
            Complex phase(std::cos(angle), std::sin(angle));
            sum += state[x] * phase;
        }
        out[y] = sum * inv_sqrt_q;
    }
    std::copy(out.begin(), out.end(), state.begin());
}

// Розклад у неперервний дріб для знаходження періоду r
std::vector<uint64_t> continued_fraction_convergents(uint64_t y, uint64_t q, uint64_t n) {
    std::vector<uint64_t> r_candidates;
    uint64_t a_num = y, a_den = q;
    int64_t p_prev2 = 0, p_prev1 = 1;
    int64_t q_prev2 = 1, q_prev1 = 0;

    while (a_den != 0) {
        uint64_t quot = a_num / a_den;
        uint64_t rem = a_num % a_den;

        int64_t p_curr = quot * p_prev1 + p_prev2;
        int64_t q_curr = quot * q_prev1 + q_prev2;

        if (q_curr >= static_cast<int64_t>(n)) break;
        if (q_curr > 0) {
            r_candidates.push_back(static_cast<uint64_t>(q_curr));
        }

        p_prev2 = p_prev1;
        p_prev1 = p_curr;
        q_prev2 = q_prev1;
        q_prev1 = q_curr;

        a_num = a_den;
        a_den = rem;
    }
    return r_candidates;
}

// Симуляція квантового пошуку періоду r для функції f(x) = a^x mod n
std::optional<uint64_t> quantum_find_period(uint64_t a, uint64_t n, std::mt19937_64& rng) {
    // Обираємо розмірність Q = 2^m >= n^2
    size_t m = 1;
    while ((1ULL << m) < n * n) ++m;
    const size_t q = 1ULL << m;

    std::vector<Complex> state(q, Complex(0.0, 0.0));

    // Моделювання вимірювання другого регістра (обрання випадкового x0)
    std::uniform_int_distribution<size_t> dist_x0(0, n);
    size_t x0 = dist_x0(rng);
    uint64_t target_val = mod_exp(a, x0, n);

    // Перший регістр колапсує у періодичну гребінку станів
    size_t count = 0;
    for (size_t x = 0; x < q; ++x) {
        if (mod_exp(a, x, n) == target_val) {
            state[x] = Complex(1.0, 0.0);
            ++count;
        }
    }
    if (count == 0) return std::nullopt;

    double norm = 1.0 / std::sqrt(static_cast<double>(count));
    for (size_t x = 0; x < q; ++x) {
        state[x] *= norm;
    }

    // Застосовуємо квантове перетворення Фур'є
    apply_inverse_qft(state);

    // Семплінг вимірювання за розподілом імовірностей |amplitude|^2
    std::vector<double> probs(q);
    for (size_t y = 0; y < q; ++y) {
        probs[y] = std::norm(state[y]);
    }

    std::discrete_distribution<size_t> dist_sample(probs.begin(), probs.end());
    size_t measured_y = dist_sample(rng);

    if (measured_y == 0) return std::nullopt;

    // Класичний розклад у неперервний дріб
    auto candidates = continued_fraction_convergents(measured_y, q, n);
    for (uint64_t cand_r : candidates) {
        if (cand_r > 1 && mod_exp(a, cand_r, n) == 1) {
            return cand_r;
        }
    }
    return std::nullopt;
}

// Повний алгоритм факторизації Шора
std::pair<uint64_t, uint64_t> shor_factorize(uint64_t n) {
    if (n % 2 == 0) return {2, n / 2};

    std::random_device rd;
    std::mt19937_64 rng(rd());
    std::uniform_int_distribution<uint64_t> dist_a(2, n - 2);

    for (int attempt = 1; attempt <= 100; ++attempt) {
        uint64_t a = dist_a(rng);
        uint64_t g = std::gcd(a, n);
        if (g > 1) {
            return {g, n / g}; // Випадковий спільний дільник
        }

        auto maybe_r = quantum_find_period(a, n, rng);
        if (!maybe_r.has_value()) continue;

        uint64_t r = maybe_r.value();
        if (r % 2 != 0) continue; // Період має бути парним

        uint64_t half_pow = mod_exp(a, r / 2, n);
        if (half_pow == n - 1) continue; // a^(r/2) != -1 mod n

        uint64_t factor1 = std::gcd(half_pow - 1, n);
        uint64_t factor2 = std::gcd(half_pow + 1, n);

        if (factor1 > 1 && factor1 < n) return {factor1, n / factor1};
        if (factor2 > 1 && factor2 < n) return {factor2, n / factor2};
    }
    return {1, n}; // Не вдалося знайти дільник за 100 спроб
}

int main() {
    uint64_t n = 15;
    auto [p, q] = shor_factorize(n);
    std::cout << "Факторизація N = " << n << " -> " << p << " * " << q << std::endl;
    return 0;
}
