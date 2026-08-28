#include "driver/gpio.h"

// Номери GPIO чипа, до яких припаяно стовпці 0..7 (катоди через резистори).
static const gpio_num_t COL_PIN[8] = {
    GPIO_NUM_4,  GPIO_NUM_5,  GPIO_NUM_12, GPIO_NUM_13,
    GPIO_NUM_14, GPIO_NUM_15, GPIO_NUM_16, GPIO_NUM_17,
};

// GPIO, що керують транзисторними ключами рядків 0..7 (аноди до +5 В).
// GPIO 6..11 зайняті флешем, 34..39 — тільки входи: під виходи не годяться.
static const gpio_num_t ROW_PIN[8] = {
    GPIO_NUM_18, GPIO_NUM_19, GPIO_NUM_21, GPIO_NUM_22,
    GPIO_NUM_23, GPIO_NUM_25, GPIO_NUM_26, GPIO_NUM_27,
};
