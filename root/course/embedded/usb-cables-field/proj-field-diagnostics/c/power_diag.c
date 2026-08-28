// power_diag.c
#include "power_diag.h"

// --- Апаратні гачки: реалізуються під конкретну плату ---
// Один сирий відлік АЦП на дільнику VBUS, у мілівольтах ВЖЕ на вході.
extern uint16_t hw_adc_vbus_mv_raw(void);
// Оцінка струму заряду в мА: шунт+підсилювач АБО регістр зарядника.
extern uint16_t hw_charge_current_ma(void);

// Усереднення VBUS: беремо 2^log2 сирих відліків і ДІЛИМО (просте середнє).
// Це давить випадковий шум АЦП у sqrt(N) разів — рівно те, що треба
// перед порівнянням із порогом, який теж у десятках мВ.
static uint16_t vbus_averaged(uint8_t log2n) {
    uint8_t  n = (uint8_t)(1u << log2n);
    uint32_t acc = 0;
    for (uint8_t i = 0; i < n; i++)
        acc += hw_adc_vbus_mv_raw();
    return (uint16_t)(acc >> log2n);   // ділення на 2^log2n = зсув
}
