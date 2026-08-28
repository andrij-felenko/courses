#include <cstdint>
#include <cstddef>

class Ring {
    static constexpr uint16_t SIZE = 256;      // степінь двійки → швидка маска
    static constexpr uint16_t MASK = SIZE - 1;

    uint8_t buf_[SIZE];
    volatile uint16_t head_ = 0;               // writer index
    volatile uint16_t tail_ = 0;               // reader index
    volatile uint16_t count_ = 0;              // зайнято байтів

public:
    // writer: true = записано, false = повно (політика «відкинути новий»)
    bool push(uint8_t b) {
        if (count_ == SIZE) return false;      // повно
        buf_[head_] = b;                       // 1) дані
        head_ = (head_ + 1) & MASK;            // 2) посунути голову
        ++count_;
        return true;
    }

    // reader: true = є байт (в out), false = порожньо
    bool pop(uint8_t &out) {
        if (count_ == 0) return false;         // порожньо
        out = buf_[tail_];
        tail_ = (tail_ + 1) & MASK;
        --count_;
        return true;
    }
};
