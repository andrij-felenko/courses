// Кожне поле, що узгоджується окремо, — на СВОЮ лінію кешу (32 байти).
typedef struct {
    __attribute__((aligned(32))) volatile uint16_t head;
    uint8_t  _p1[32 - sizeof(uint16_t)];      // добити лінію до кінця

    __attribute__((aligned(32))) volatile uint16_t tail;
    uint8_t  _p2[32 - sizeof(uint16_t)];

    __attribute__((aligned(32))) slot_t slot[SLOTS];   // слоти — з нової лінії
} mailbox_aligned_t;
