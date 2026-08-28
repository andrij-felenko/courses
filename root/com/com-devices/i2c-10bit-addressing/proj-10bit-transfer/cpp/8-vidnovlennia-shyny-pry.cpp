#include <functional>
#include <cstdint>

class I2cBusRecovery {
public:
    struct PinOps {
        std::function<void(bool)> setScl;
        std::function<bool()> getSda;
        std::function<void(bool)> setSda;
        std::function<void(uint32_t)> delayUs;
    };

    static bool recover(const PinOps& ops) noexcept {
        ops.setSda(true);
        ops.delayUs(5);

        for (int i = 0; i < 9; ++i) {
            if (ops.getSda()) {
                break;
            }
            ops.setScl(false);
            ops.delayUs(5);
            ops.setScl(true);
            ops.delayUs(5);
        }

        // Формування аварійного сигналу STOP
        ops.setSda(false);
        ops.delayUs(5);
        ops.setScl(true);
        ops.delayUs(5);
        ops.setSda(true);
        ops.delayUs(5);

        return ops.getSda();
    }
};
