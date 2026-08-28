/* Вісім виводів під сегменти налаштовано в CubeMX як GPIO_Output (push-pull),
   такт порту вже піднято в MX_GPIO_Init(). Спільний катод: SET = світиться. */
typedef struct { GPIO_TypeDef *port; uint16_t pin; } seg_line_t;

static const seg_line_t SEG[8] = {                      // a b c d e f g DP
    { GPIOA, GPIO_PIN_0 }, { GPIOA, GPIO_PIN_1 }, { GPIOA, GPIO_PIN_2 }, { GPIOA, GPIO_PIN_3 },
    { GPIOA, GPIO_PIN_4 }, { GPIOA, GPIO_PIN_5 }, { GPIOA, GPIO_PIN_6 }, { GPIOA, GPIO_PIN_7 },
};

// Маски цифр 0..9. Біт 0 = a, біт 1 = b, ... біт 6 = g, біт 7 = DP.
static const uint8_t DIGIT[10] = {
    0b00111111, 0b00000110, 0b01011011, 0b01001111, 0b01100110,   // 0 1 2 3 4
    0b01101101, 0b01111101, 0b00000111, 0b01111111, 0b01101111,   // 5 6 7 8 9
};

void Seg_Show(uint8_t d, bool dot) {
    uint8_t mask = DIGIT[d];
    if (dot) mask |= 0b10000000;                        // засвітити крапку
    for (int i = 0; i < 8; i++)
        HAL_GPIO_WritePin(SEG[i].port, SEG[i].pin,
                          ((mask >> i) & 1) ? GPIO_PIN_SET : GPIO_PIN_RESET);
}

/* у нескінченному циклі main() */
while (1) {
    for (uint8_t d = 0; d < 10; d++) { Seg_Show(d, false); HAL_Delay(700); }
}
