#include <iostream>
#include <vector>
#include <unordered_map>
#include <cmath>
#include <cstdint>
#include <stdexcept>
#include <numeric>
#include <cassert>

// 128-бітний беззнаковий цілий тип для безпечного проміжного множення
using uint128 = unsigned __int128;

// Швидке модульне піднесення до степеня (base^exp mod mod)
std::uint64_t mod_pow(std::uint64_t base, std::uint64_t exp, std::uint64_t mod) {
    std::uint64_t res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) {
            res = static_cast<std::uint64_t>((static_cast<uint128>(res) * base) % mod);
        }
        base = static_cast<std::uint64_t>((static_cast<uint128>(base) * base) % mod);
        exp >>= 1;
    }
    return res;
}

// Розширений алгоритм Евкліда: знаходить g, x, y такі, що a*x + b*y = g
std::int64_t ext_gcd(std::int64_t a, std::int64_t b, std::int64_t& x, std::int64_t& y) {
    if (b == 0) {
        x = 1;
        y = 0;
        return a;
    }
    std::int64_t x1 = 0, y1 = 0;
    std::int64_t g = ext_gcd(b, a % b, x1, y1);
    x = y1;
    y = x1 - (a / b) * y1;
    return g;
}

// Обчислення мультиплікативного оберненого елемента a^(-1) mod mod
std::uint64_t mod_inv(std::uint64_t a, std::uint64_t mod) {
    std::int64_t x = 0, y = 0;
    std::int64_t g = ext_gcd(static_cast<std::int64_t>(a), static_cast<std::int64_t>(mod), x, y);
    if (g != 1) {
        throw std::runtime_error("Елемент не має оберненого за заданим модулем");
    }
    return static_cast<std::uint64_t>((x % static_cast<std::int64_t>(mod) + mod) % mod);
}

// Алгоритм Baby-Step Giant-Step для знаходження логарифма у підгрупі простого порядку
std::uint64_t solve_dlog_bsgs(std::uint64_t g, std::uint64_t h, std::uint64_t p_order, std::uint64_t mod) {
    std::uint64_t m = static_cast<std::uint64_t>(std::sqrt(p_order)) + 1;
    std::unordered_map<std::uint64_t, std::uint64_t> table;
    table.reserve(m);

    // Baby steps: g^j mod mod
    std::uint64_t cur = 1;
    for (std::uint64_t j = 0; j < m; ++j) {
        table.try_emplace(cur, j);
        cur = static_cast<std::uint64_t>((static_cast<uint128>(cur) * g) % mod);
    }

    // Giant steps: factor = g^(-m) mod mod
    std::uint64_t g_m = mod_pow(g, m, mod);
    std::uint64_t factor = mod_inv(g_m, mod);

    std::uint64_t gamma = h % mod;
    for (std::uint64_t i = 0; i < m; ++i) {
        auto it = table.find(gamma);
        if (it != table.end()) {
            std::uint64_t x = i * m + it->second;
            if (x < p_order) return x;
        }
        gamma = static_cast<std::uint64_t>((static_cast<uint128>(gamma) * factor) % mod);
    }

    throw std::runtime_error("Дискретний логарифм у підгрупі не знайдено");
}

// Порозрядний ліфтинг для знаходження логарифма у підгрупі порядку p^e
std::uint64_t solve_prime_power(std::uint64_t g, std::uint64_t h, std::uint64_t p, std::uint32_t e,
                                std::uint64_t n, std::uint64_t mod) {
    std::uint64_t p_e = 1;
    for (std::uint32_t i = 0; i < e; ++i) p_e *= p;

    // 1. Проекція генератора та цілі на підгрупу порядку p^e
    std::uint64_t proj_exp = n / p_e;
    std::uint64_t g_sub = mod_pow(g, proj_exp, mod);
    std::uint64_t h_sub = mod_pow(h, proj_exp, mod);

    // 2. Базовий генератор підгрупи простого порядку p
    std::uint64_t p_e_minus_1 = p_e / p;
    std::uint64_t gamma = mod_pow(g_sub, p_e_minus_1, mod);
    std::uint64_t g_sub_inv = mod_inv(g_sub, mod);

    // 3. Порозрядне вилучення цифр
    std::uint64_t x = 0;
    std::uint64_t p_pow_j = 1;

    for (std::uint32_t j = 0; j < e; ++j) {
        std::uint64_t g_inv_x = mod_pow(g_sub_inv, x, mod);
        std::uint64_t h_cur = static_cast<std::uint64_t>((static_cast<uint128>(h_sub) * g_inv_x) % mod);

        std::uint64_t iso_exp = 1;
        for (std::uint32_t k = 0; k < e - 1 - j; ++k) iso_exp *= p;

        std::uint64_t target = mod_pow(h_cur, iso_exp, mod);
        std::uint64_t z_j = solve_dlog_bsgs(gamma, target, p, mod);

        x += z_j * p_pow_j;
        p_pow_j *= p;
    }

    return x;
}

// Китайська теорема про залишки (CRT)
std::uint64_t crt(const std::vector<std::uint64_t>& rem, const std::vector<std::uint64_t>& mod_list) {
    std::uint64_t total_m = 1;
    for (auto m : mod_list) total_m *= m;

    std::uint64_t x = 0;
    for (std::size_t i = 0; i < rem.size(); ++i) {
        std::uint64_t m_i = total_m / mod_list[i];
        std::uint64_t inv = mod_inv(m_i, mod_list[i]);
        uint128 term = (static_cast<uint128>(rem[i]) * m_i) % total_m;
        term = (term * inv) % total_m;
        x = static_cast<std::uint64_t>((x + term) % total_m);
    }
    return x;
}

// Головна функція алгоритму Поліга — Геллмана
std::uint64_t pohlig_hellman(std::uint64_t g, std::uint64_t h, std::uint64_t n,
                             const std::vector<std::pair<std::uint64_t, std::uint32_t>>& factors,
                             std::uint64_t mod) {
    std::vector<std::uint64_t> rems;
    std::vector<std::uint64_t> moduli;

    for (const auto& [p, e] : factors) {
        std::uint64_t p_e = 1;
        for (std::uint32_t i = 0; i < e; ++i) p_e *= p;

        std::uint64_t x_i = solve_prime_power(g, h, p, e, n, mod);
        rems.push_back(x_i);
        moduli.push_back(p_e);
    }

    return crt(rems, moduli);
}

int main() {
    // Тест 1: Група Z_31^* (модуль 31, порядок 30 = 2^1 * 3^1 * 5^1)
    std::uint64_t p_mod = 31;
    std::uint64_t n_order = 30;
    std::vector<std::pair<std::uint64_t, std::uint32_t>> prime_factors = {{2, 1}, {3, 1}, {5, 1}};
    std::uint64_t generator = 3;
    std::uint64_t target_val = 13;

    std::uint64_t solved_x = pohlig_hellman(generator, target_val, n_order, prime_factors, p_mod);
    std::cout << "[C++ Тест 1: Z_31^*] Знайдений показник x = " << solved_x << "\n";
    std::cout << "Перевірка: " << generator << "^" << solved_x << " mod " << p_mod
              << " = " << mod_pow(generator, solved_x, p_mod) << " (очікувалось: " << target_val << ")\n";
    assert(mod_pow(generator, solved_x, p_mod) == target_val);

    // Тест 2: Група з кратним степенем Z_17^* (порядок 16 = 2^4)
    std::uint64_t p_mod2 = 17;
    std::uint64_t n_order2 = 16;
    std::vector<std::pair<std::uint64_t, std::uint32_t>> prime_factors2 = {{2, 4}};
    std::uint64_t generator2 = 3;
    std::uint64_t target_val2 = 11;

    std::uint64_t solved_x2 = pohlig_hellman(generator2, target_val2, n_order2, prime_factors2, p_mod2);
    std::cout << "[C++ Тест 2: Z_17^*] Знайдений показник x = " << solved_x2 << "\n";
    std::cout << "Перевірка: " << generator2 << "^" << solved_x2 << " mod " << p_mod2
              << " = " << mod_pow(generator2, solved_x2, p_mod2) << " (очікувалось: " << target_val2 << ")\n";
    assert(mod_pow(generator2, solved_x2, p_mod2) == target_val2);

    std::cout << "Усі перевірки C++ пройдено успішно!\n";
    return 0;
}
