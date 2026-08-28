#include <vector>
#include <cstdint>
#include <span>
#include <expected>
#include <algorithm>

struct RsaCrtKey {
    std::vector<uint64_t> p;       // Простий множник p
    std::vector<uint64_t> q;       // Простий множник q
    std::vector<uint64_t> dp;      // dp = d mod (p - 1)
    std::vector<uint64_t> dq;      // dq = d mod (q - 1)
    std::vector<uint64_t> qinv;    // qinv = q^(-1) mod p
    size_t limbs_half{0};
};

enum class RsaError {
    InvalidKeyLength,
    ComputationError
};

// Зовнішні інтерфейси оптимізованого рушія модульної арифметики
void bigint_mod_exp(std::span<uint64_t> res, std::span<const uint64_t> base,
                    std::span<const uint64_t> exp, std::span<const uint64_t> mod);
void bigint_sub_mod(std::span<uint64_t> res, std::span<const uint64_t> a,
                    std::span<const uint64_t> b, std::span<const uint64_t> mod);
void bigint_mul_mod(std::span<uint64_t> res, std::span<const uint64_t> a,
                    std::span<const uint64_t> b, std::span<const uint64_t> mod);
void bigint_mul_add(std::span<uint64_t> res, std::span<const uint64_t> mq,
                    std::span<const uint64_t> h, std::span<const uint64_t> q);

// Ідіоматична функція розшифрування RSA-CRT
std::expected<std::vector<uint64_t>, RsaError>
rsa_crt_decrypt(std::span<const uint64_t> ciphertext, const RsaCrtKey& key) {
    const size_t n = key.limbs_half;
    if (key.p.size() != n || key.q.size() != n || key.dp.size() != n ||
        key.dq.size() != n || key.qinv.size() != n) {
        return std::unexpected(RsaError::InvalidKeyLength);
    }

    std::vector<uint64_t> mp(n);
    std::vector<uint64_t> mq(n);
    std::vector<uint64_t> diff(n);
    std::vector<uint64_t> h(n);
    std::vector<uint64_t> plaintext(2 * n, 0);

    // 1. Обчислення залишків mp = c^dp mod p та mq = c^dq mod q
    bigint_mod_exp(mp, ciphertext, key.dp, key.p);
    bigint_mod_exp(mq, ciphertext, key.dq, key.q);

    // 2. Реконструкція Garner: h = (qinv * (mp - mq)) mod p
    bigint_sub_mod(diff, mp, mq, key.p);
    bigint_mul_mod(h, diff, key.qinv, key.p);

    // 3. Збирання повного 2048-бітного відкритого тексту m = mq + h * q
    bigint_mul_add(plaintext, mq, h, key.q);

    return plaintext;
}
