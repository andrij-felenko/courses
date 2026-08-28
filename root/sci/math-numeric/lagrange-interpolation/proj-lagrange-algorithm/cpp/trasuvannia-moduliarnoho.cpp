#include <iostream>
#include <vector>
#include <span>
#include <cstdint>

constexpr int64_t MOD_P = 1000000007LL;

static int64_t power_mod(int64_t base, int64_t exp) {
    int64_t res = 1;
    base %= MOD_P;
    while (exp > 0) {
        if (exp % 2 == 1) res = static_cast<__int128>(res) * base % MOD_P;
        base = static_cast<__int128>(base) * base % MOD_P;
        exp /= 2;
    }
    return res;
}

static int64_t mod_inverse(int64_t n) {
    return power_mod(n, MOD_P - 2);
}

[[nodiscard]] int64_t gf_lagrange_reconstruct_secret(
    std::span<const int64_t> x_shares, 
    std::span<const int64_t> y_shares) 
{
    const size_t k = x_shares.size();
    int64_t secret = 0;

    for (size_t i = 0; i < k; ++i) {
        int64_t num = 1;
        int64_t den = 1;

        for (size_t j = 0; j < k; ++j) {
            if (i != j) {
                num = static_cast<__int128>(num) * (MOD_P - x_shares[j]) % MOD_P;
                int64_t diff = (x_shares[i] - x_shares[j] + MOD_P) % MOD_P;
                den = static_cast<__int128>(den) * diff % MOD_P;
            }
        }

        int64_t term = static_cast<__int128>(y_shares[i]) * num % MOD_P;
        term = static_cast<__int128>(term) * mod_inverse(den) % MOD_P;
        secret = (secret + term) % MOD_P;
    }

    return secret;
}

int main() {
    std::vector<int64_t> x = {1, 2, 3};
    std::vector<int64_t> y = {14892, 45293, 91216};

    int64_t secret = gf_lagrange_reconstruct_secret(x, y);
    std::cout << "C++ GF(p) Відновлений секрет = " << secret << "\n";
    return 0;
}
