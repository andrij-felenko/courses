#include <cstdint>

class EmaFx {
    static constexpr int Q = 8;      // стільки дробових біт тримає acc
    std::int32_t acc = 0;            // оцінка у форматі з фіксованою комою (<<Q)
    std::int32_t a_num;              // α = a_num / 256
    bool primed = false;

public:
    explicit EmaFx(std::int32_t num) : a_num(num) {}  // напр. num=26 ≈ α 0.1

    std::int32_t step(std::int32_t x) {
        if (!primed) {
            acc = x << Q;                    // старт першим відліком
            primed = true;
        } else {
            std::int32_t err = (x << Q) - acc;  // різниця у тому ж масштабі
            acc += (a_num * err) >> 8;          // + α·(x − y), знаменник 256
        }
        return acc >> Q;                     // назовні — звичайне число
    }
};
