#include <iostream>
#include <unordered_map>
#include "cantor_pairing.hpp"

/* Сценарій C++20: Кешування предикатів переходів станів автомата */
class StateTransitionCache {
private:
    std::unordered_map<uint64_t, bool> cache_;

public:
    bool query_transition(uint32_t state_a, uint32_t state_b) {
        auto key_opt = pairing::cantor_encode(state_a, state_b);
        if (!key_opt) {
            return false; /* Захист від переповнення */
        }

        uint64_t key = *key_opt;
        if (auto it = cache_.find(key); it != cache_.end()) {
            return it->second;
        }

        /* Обчислюємо предикат переходу */
        bool result = (state_a + state_b) % 7 == 0;
        cache_[key] = result;
        return result;
    }
};
