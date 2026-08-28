#include <random>

// Ідіоматична C++ альтернатива через власний клас-генератор LCG
class LcgEngine {
public:
    using result_type = uint32_t;

    explicit LcgEngine(uint32_t seed = 1) : state_(seed) {}

    static constexpr result_type min() { return 0; }
    static constexpr result_type max() { return 32767; }

    result_type operator()() {
        state_ = state_ * 1103515245U + 12345U;
        return (state_ / 65536U) % 32768U;
    }

private:
    uint32_t state_;
};
