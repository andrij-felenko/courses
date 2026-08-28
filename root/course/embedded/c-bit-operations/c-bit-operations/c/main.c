#include <stdint.h>

// іменовані маски — код читається як даташит, без магічних чисел
#define STATUS_READY    (1 << 7)   // 0b10000000
#define STATUS_OVERHEAT (1 << 6)   // 0b01000000
#define MODE_MASK       0x07       // 0b00000111 — молодші три біти

void parse_status(uint8_t status) {
    uint8_t ready    = (status & STATUS_READY)    != 0;   // 0 або 1
    uint8_t overheat = (status & STATUS_OVERHEAT) != 0;   // 0 або 1
    uint8_t mode     =  status & MODE_MASK;               // число 0…7

    if (ready && !overheat) {
        // дані свіжі й перегріву нема — можна користуватися вимірюванням
    }
}
