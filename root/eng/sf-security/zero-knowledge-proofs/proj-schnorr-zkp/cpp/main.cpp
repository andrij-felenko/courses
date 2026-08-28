#include <iostream>
#include <optional>
#include <stdexcept>
#include <cstdint>

namespace zk {

/* Математичні криптографічні параметри групи */
struct GroupParams {
    std::int64_t mod_p{23};
    std::int64_t order_q{11};
    std::int64_t generator_g{2};
};

/* Специфікація транскрипту Шнорра */
struct Transcript {
    std::int64_t commitment_R;
    std::int64_t challenge_e;
    std::int64_t response_s;
};

class SchnorrProtocol {
private:
    GroupParams params_;

public:
    explicit SchnorrProtocol(GroupParams params = {}) : params_(params) {}

    [[nodiscard]] std::int64_t power_mod(std::int64_t base, std::int64_t exp, std::int64_t mod) const {
        std::int64_t res = 1;
        base %= mod;
        while (exp > 0) {
            if (exp & 1) res = (res * base) % mod;
            base = (base * base) % mod;
            exp >>= 1;
        }
        return res;
    }

    [[nodiscard]] std::int64_t mod_inverse(std::int64_t a, std::int64_t m) const {
        std::int64_t m0 = m, t{}, q{};
        std::int64_t x0 = 0, x1 = 1;
        if (m == 1) return 0;
        while (a > 1) {
            q = a / m;
            t = m;
            m = a % m;
            a = t;
            t = x0;
            x0 = x1 - q * x0;
            x1 = t;
        }
        if (x1 < 0) x1 += m0;
        return x1;
    }

    /* Верифікація транскрипту: g^s == R * Y^e (mod p) */
    [[nodiscard]] bool verify(std::int64_t public_Y, const Transcript& t) const {
        std::int64_t left = power_mod(params_.generator_g, t.response_s, params_.mod_p);
        std::int64_t Y_e = power_mod(public_Y, t.challenge_e, params_.mod_p);
        std::int64_t right = (t.commitment_R * Y_e) % params_.mod_p;
        return left == right;
    }

    /* Інтерактивний доводжувач (Prover) */
    [[nodiscard]] Transcript prove(std::int64_t secret_x, std::int64_t random_r, std::int64_t challenge_e) const {
        std::int64_t R = power_mod(params_.generator_g, random_r, params_.mod_p);
        std::int64_t s = (random_r + challenge_e * secret_x) % params_.order_q;
        return Transcript{R, challenge_e, s};
    }

    /* Симулятор (Simulator) — генерує валідний транскрипт БЕЗ secrets */
    [[nodiscard]] Transcript simulate(std::int64_t public_Y, std::int64_t sim_e, std::int64_t sim_s) const {
        std::int64_t g_s = power_mod(params_.generator_g, sim_s, params_.mod_p);
        std::int64_t Y_e = power_mod(public_Y, sim_e, params_.mod_p);
        std::int64_t inv_Y_e = mod_inverse(Y_e, params_.mod_p);
        std::int64_t R_sim = (g_s * inv_Y_e) % params_.mod_p;
        return Transcript{R_sim, sim_e, sim_s};
    }

    /* Екстрактор знань (Knowledge Extractor) */
    [[nodiscard]] std::optional<std::int64_t> extract(const Transcript& t1, const Transcript& t2) const {
        if (t1.commitment_R != t2.commitment_R || t1.challenge_e == t2.challenge_e) {
            return std::nullopt;
        }
        std::int64_t delta_s = (t1.response_s - t2.response_s + params_.order_q) % params_.order_q;
        std::int64_t delta_e = (t1.challenge_e - t2.challenge_e + params_.order_q) % params_.order_q;
        std::int64_t inv_delta_e = mod_inverse(delta_e, params_.order_q);
        return (delta_s * inv_delta_e) % params_.order_q;
    }
};

} // namespace zk

int main() {
    zk::GroupParams params;
    zk::SchnorrProtocol protocol(params);

    constexpr std::int64_t secret_x = 7;
    const std::int64_t public_Y = protocol.power_mod(params.generator_g, secret_x, params.mod_p);

    std::cout << "[C++ ZK Engine] Публічний ключ Y = " << public_Y << '\n';

    // 1. Чесна взаємодія
    auto t1 = protocol.prove(secret_x, 4, 3);
    bool is_valid = protocol.verify(public_Y, t1);
    std::cout << "[C++ Real Proof] Валідність доказу: " << std::boolalpha << is_valid << '\n';

    // 2. Симуляція без секрету
    auto sim_t = protocol.simulate(public_Y, 5, 9);
    bool is_sim_valid = protocol.verify(public_Y, sim_t);
    std::cout << "[C++ Simulator] Валідність симульованого доказу: " << is_sim_valid << '\n';

    // 3. Екстракція секрету
    auto t2 = protocol.prove(secret_x, 4, 8);
    auto extracted = protocol.extract(t1, t2);
    if (extracted.has_value()) {
        std::cout << "[C++ Extractor] Відновлений секрет x = " << extracted.value() << '\n';
    }

    return 0;
}
