// Ноги, що керують катодними ключами розрядів. [0]=DIG1 (ліва цифра) ... [3]=DIG4.
static const SegPin CAT[4] = {
    { &PORTC, 1u << 2 },   // DIG1
    { &PORTC, 1u << 3 },   // DIG2
    { &PORTD, 1u << 3 },   // DIG3
    { &PORTD, 1u << 4 },   // DIG4
};

// Погасити ВСІ розряди: закрити всі катодні ключі.
static void all_digits_off(void)
{
    for (uint8_t i = 0; i < 4; i++)
        *CAT[i].port &= ~CAT[i].mask;   // нога у «0» → ключ закритий → розряд темний
}

// Відкрити РІВНО ОДИН розряд d (0..3): його ключ увімкнути.
static void digit_on(uint8_t d)
{
    *CAT[d].port |= CAT[d].mask;        // нога у «1» → ключ відкритий → розряд світиться
}
