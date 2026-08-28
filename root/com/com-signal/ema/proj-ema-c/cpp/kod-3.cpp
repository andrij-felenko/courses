#include <cstdint>

class EmaPow2 {
    static constexpr int SHIFT = 3;  // α = 1/2^SHIFT (SHIFT=3 → α = 1/8)
    static constexpr int Q     = 8;  // стільки дробових біт тримає acc
    std::int32_t acc = 0;            // оцінка у форматі з фіксованою комою (<<Q)
    bool primed = false;

public:
    std::int32_t step(std::int32_t x) {
        if (!primed) {
            acc = x << Q;                    // старт першим відліком
            primed = true;
        } else {
            std::int32_t err = (x << Q) - acc;  // різниця у тому ж масштабі
            acc += err >> SHIFT;                // α·(x − y) — самий зсув, без множення
        }
        return acc >> Q;                     // назовні — звичайне число
    }
};
