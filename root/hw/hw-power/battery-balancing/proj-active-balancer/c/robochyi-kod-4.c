void gate_high(bool on);   // драйвер верхнього ключа напівмоста
void gate_low(bool on);    // драйвер нижнього ключа напівмоста

// напівміст індуктивного (buck-boost) балансира: між фазами — той самий зазор
void halfbridge_drive(bool high_side)
{
    gate_high(false);                     // розімкнути ОБИДВА,
    gate_low(false);
    delay_ns(DEADTIME_NS);                // витримати мертвий час,
    if (high_side) gate_high(true);       // тоді замкнути лише потрібний
    else           gate_low(true);
}
