#include "core_cm4.h"          // CMSIS: структура MPU й біти-маски

// AP-кодування (ARMv7-M): привілейований / непривілейований
#define AP_RW_RW   (0x3u << MPU_RASR_AP_Pos)   // обом: читати й писати
#define AP_RO_RO   (0x6u << MPU_RASR_AP_Pos)   // обом: тільки читати
#define SZ(n)      (((n) - 1) << MPU_RASR_SIZE_Pos)  // розмір = 2ⁿ байтів

static void region_set(uint32_t idx, uint32_t base,
                       uint32_t size_bits, uint32_t attrs) {
    MPU->RNR  = idx;                         // яку область описуємо
    MPU->RBAR = base & MPU_RBAR_ADDR_Msk;    // база (кратна розмірові!)
    MPU->RASR = MPU_RASR_ENABLE_Msk | size_bits | attrs |
                MPU_RASR_XN_Msk;             // + заборона виконання
}

void mpu_setup(void) {
    MPU->CTRL = 0;                           // 1) вимкнути на час налаштування
    __DSB(); __ISB();

    // 2) Область 0: уся RAM 128 КБ — читати й писати
    region_set(0, 0x20000000u, SZ(17), AP_RW_RW);   // 2¹⁷ = 128 КБ

    // 3) Область 1 (старша!): 1 КБ таблиці констант — тільки читати
    region_set(1, 0x2000F000u, SZ(10), AP_RO_RO);   // 2¹⁰ = 1 КБ

    // 4) увімкнути MPU; PRIVDEFENA лишає привілейованому доступ
    //    до решти карти за замовчуванням, поза описаними областями
    MPU->CTRL = MPU_CTRL_ENABLE_Msk | MPU_CTRL_PRIVDEFENA_Msk;
    __DSB(); __ISB();                        // дочекатись, поки набуде сили
}
