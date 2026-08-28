#include <iostream>
#include <string_view>
#include <vector>

void rabin_karp_search(std::string_view pat, std::string_view txt) {
    const size_t m = pat.size();
    const size_t n = txt.size();
    if (m > n || m == 0) return;

    constexpr long long base = 256;
    constexpr long long mod = 101;

    long long p_hash = 0;
    long long t_hash = 0;
    long long h = 1;

    for (size_t i = 0; i < m - 1; ++i) {
        h = (h * base) % mod;
    }

    for (size_t i = 0; i < m; ++i) {
        p_hash = (base * p_hash + pat[i]) % mod;
        t_hash = (base * t_hash + txt[i]) % mod;
    }

    for (size_t i = 0; i <= n - m; ++i) {
        if (p_hash == t_hash) {
            if (txt.substr(i, m) == pat) {
                std::cout << "Точний збіг на позиції: " << i << "\n";
            } else {
                std::cout << "Колізія хешу Діріхле на позиції: " << i << "\n";
            }
        }
        if (i < n - m) {
            t_hash = (base * (t_hash - txt[i] * h) + txt[i + m]) % mod;
            if (t_hash < 0) t_hash += mod;
        }
    }
}

int main() {
    std::string_view text = "ABABDABACDABABCABAB";
    std::string_view pattern = "ABABC";
    rabin_karp_search(pattern, text);
    return 0;
}
