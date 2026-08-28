#include "pow_mod.h"

namespace MathLib {
    // Спеціалізація для uint64_t
    template <>
    uint64_t pow_mod<uint64_t>(uint64_t base, uint64_t exponent, uint64_t mod) {
        if (mod == 0) {
            throw std::invalid_argument("Modulo cannot be zero");
        }
        if (mod == 1) {
            return 0; // Будь-яке число mod 1 дорівнює 0
        }

        uint64_t result = 1;
        base = base % mod;

        while (exponent > 0) {
            // Перевіряємо наймолодший біт (еквівалент exponent % 2 == 1)
            if (exponent & 1) {
                result = Utils::mul_mod(result, base, mod);
            }
            
            // Піднесення основи до квадрата
            base = Utils::mul_mod(base, base, mod);
            
            // Зсуваємо показник на 1 біт вправо (еквівалент exponent / 2)
            exponent >>= 1;
        }

        return result;
    }
}
