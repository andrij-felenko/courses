#include <cstdint>

struct DmaStreamRegisters {
    volatile uint32_t CR;
    volatile uint32_t NDTR;
    volatile uint32_t PAR;
    volatile uint32_t M0AR;
};

class DmaAbortGuard {
public:
    static bool abort(DmaStreamRegisters* stream, const DwtTimeout& timeout) noexcept {
        constexpr uint32_t STREAM_EN = (1UL << 0);
        stream->CR &= ~STREAM_EN;

        while ((stream->CR & STREAM_EN) != 0) {
            if (timeout.expired()) {
                return false;
            }
        }
        return true;
    }
};
