#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <memory>
#include <numeric>

class LWEEngine {
public:
    static constexpr int N = 32;
    static constexpr int M = 64;
    static constexpr int Q = 3329;
    static constexpr double SIGMA = 2.0;

    struct SecretKey {
        std::vector<int> s;
        SecretKey() : s(N) {}
    };

    struct PublicKey {
        std::vector<std::vector<int>> A;
        std::vector<int> b;
        PublicKey() : A(M, std::vector<int>(N)), b(M) {}
    };

    struct Ciphertext {
        std::vector<int> c1;
        int c2;
        Ciphertext() : c1(N), c2(0) {}
    };

    LWEEngine() : rng(std::random_device{}()) {}

    void keygen(PublicKey& pk, SecretKey& sk) {
        std::uniform_int_distribution<int> dist_q(0, Q - 1);
        std::normal_distribution<double> dist_gauss(0.0, SIGMA);

        for (int j = 0; j < N; ++j) {
            sk.s[j] = dist_q(rng);
        }

        for (int i = 0; i < M; ++i) {
            long long ax = 0;
            for (int j = 0; j < N; ++j) {
                pk.A[i][j] = dist_q(rng);
                ax = (ax + static_cast<long long>(pk.A[i][j]) * sk.s[j]) % Q;
            }
            int noise = static_cast<int>(std::round(dist_gauss(rng)));
            pk.b[i] = mod_q(static_cast<int>(ax) + noise);
        }
    }

    Ciphertext encrypt(const PublicKey& pk, int bit) {
        Ciphertext ct;
        std::uniform_int_distribution<int> dist_bin(0, 1);
        std::vector<int> r(M);
        for (int i = 0; i < M; ++i) r[i] = dist_bin(rng);

        for (int j = 0; j < N; ++j) {
            long long sum = 0;
            for (int i = 0; i < M; ++i) {
                sum = (sum + static_cast<long long>(pk.A[i][j]) * r[i]) % Q;
            }
            ct.c1[j] = static_cast<int>(sum);
        }

        long long b_r = 0;
        for (int i = 0; i < M; ++i) {
            b_r = (b_r + static_cast<long long>(pk.b[i]) * r[i]) % Q;
        }
        int scale = (bit == 1) ? (Q / 2) : 0;
        ct.c2 = mod_q(static_cast<int>(b_r) + scale);
        return ct;
    }

    int decrypt(const Ciphertext& ct, const SecretKey& sk) const {
        long long c1_s = 0;
        for (int j = 0; j < N; ++j) {
            c1_s = (c1_s + static_cast<long long>(ct.c1[j]) * sk.s[j]) % Q;
        }
        int diff = mod_q(ct.c2 - static_cast<int>(c1_s));

        int dist_to_half = std::abs(diff - Q / 2);
        return (dist_to_half < Q / 4) ? 1 : 0;
    }

private:
    static inline int mod_q(int x) {
        int r = x % Q;
        return (r < 0) ? (r + Q) : r;
    }

    std::mt19937 rng;
};

int main() {
    LWEEngine engine;
    LWEEngine::SecretKey sk;
    LWEEngine::PublicKey pk;

    engine.keygen(pk, sk);

    std::vector<int> test_bits = {1, 0, 1, 1, 0, 0, 1, 0};
    std::cout << "--- Тест C++ LWE Engine ---\n";

    for (size_t i = 0; i < test_bits.size(); ++i) {
        auto ct = engine.encrypt(pk, test_bits[i]);
        int decrypted = engine.decrypt(ct, sk);
        std::cout << "Bit " << i << ": Input = " << test_bits[i] 
                  << ", Decrypted = " << decrypted 
                  << " [" << (test_bits[i] == decrypted ? "OK" : "FAIL") << "]\n";
    }

    return 0;
}
