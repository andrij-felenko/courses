#include <iostream>
#include <numeric>
#include <random>
#include <stdexcept>

// Тип для демо-обчислень (у реальних проектах використовується Boost.Multiprecision або OpenSSL BIGNUM)
using int64 = long long;
using int128 = __int128_t;

int64 extended_gcd(int64 a, int64 b, int64& x, int64& y) {
    if (a == 0) {
        x = 0; y = 1;
        return b;
    }
    int64 x1, y1;
    int64 d = extended_gcd(b % a, a, x1, y1);
    x = y1 - (b / a) * x1;
    y = x1;
    return d;
}

int64 mod_inverse(int64 a, int64 m) {
    int64 x, y;
    int64 g = extended_gcd(a, m, x, y);
    if (g != 1) {
        throw std::invalid_argument("Модульний інверс не існує");
    }
    return (x % m + m) % m;
}

int64 mod_pow(int64 base, int64 exp, int64 mod) {
    int64 res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp % 2 == 1) res = (static_cast<int128>(res) * base) % mod;
        base = (static_cast<int128>(base) * base) % mod;
        exp /= 2;
    }
    return res;
}

int64 lcm(int64 a, int64 b) {
    return (a / std::gcd(a, b)) * b;
}

class PaillierPublicKey {
public:
    int64 n;
    int64 n_sq;

    explicit PaillierPublicKey(int64 n_val) : n(n_val), n_sq(n_val * n_val) {}

    int64 encrypt(int64 m) const {
        int64 m_mod = (m % n + n) % n;
        
        // Генеруємо випадковий шум r
        std::random_device rd;
        std::mt19937_64 gen(rd());
        std::uniform_int_distribution<int64> dis(1, n - 1);
        
        int64 r = 1;
        do {
            r = dis(gen);
        } while (std::gcd(r, n) != 1);

        int64 c_msg = (1 + m_mod * n) % n_sq;
        int64 c_rnd = mod_pow(r, n, n_sq);

        return (static_cast<int128>(c_msg) * c_rnd) % n_sq;
    }

    int64 add(int64 c1, int64 c2) const {
        return (static_cast<int128>(c1) * c2) % n_sq;
    }

    int64 mul_scalar(int64 c, int64 k) const {
        if (k < 0) {
            c = mod_inverse(c, n_sq);
            k = -k;
        }
        return mod_pow(c, k, n_sq);
    }
};

class PaillierPrivateKey {
private:
    int64 p, q;
    int64 lam;
    int64 mu;

public:
    PaillierPublicKey pub;

    PaillierPrivateKey(int64 p_val, int64 q_val)
        : p(p_val), q(q_val), pub(p_val * q_val) {
        int64 n = pub.n;
        lam = lcm(p - 1, q - 1);
        mu = mod_inverse(lam, n);
    }

    int64 decrypt(int64 c) const {
        int64 u = mod_pow(c, lam, pub.n_sq);
        int64 l_u = (u - 1) / pub.n;
        int64 m = (static_cast<int128>(l_u) * mu) % pub.n;

        if (m > pub.n / 2) {
            m -= pub.n;
        }
        return m;
    }
};

int main() {
    int64 p = 61, q = 53;
    PaillierPrivateKey key(p, q);

    std::cout << "n = " << key.pub.n << ", n^2 = " << key.pub.n_sq << std::endl;

    int64 c1 = key.pub.encrypt(15);
    int64 c2 = key.pub.encrypt(27);

    // Гомоморфне додавання 15 + 27
    int64 c_sum = key.pub.add(c1, c2);
    std::cout << "Розшифрована сума (15 + 27): " << key.decrypt(c_sum) << std::endl;

    // Гомоморфне множення 15 на скаляр 3
    int64 c_scaled = key.pub.mul_scalar(c1, 3);
    std::cout << "Розшифрований добуток (15 * 3): " << key.decrypt(c_scaled) << std::endl;

    return 0;
}
