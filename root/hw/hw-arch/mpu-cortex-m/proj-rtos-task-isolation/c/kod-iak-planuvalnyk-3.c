// Помічник: спакувати опис області у формат RBAR+RASR один раз при старті.
// size_pow2 — показник степеня: 10 → 1 КБ (2¹⁰), 11 → 2 КБ, …
static MpuRegion make_region(uint32_t region_num, uint32_t base,
                             uint32_t size_pow2, uint32_t ap, int exec)
{
    MpuRegion r;
    // RBAR: база (кратна розмірові!) + VALID + номер області в молодших бітах
    r.rbar = (base & MPU_RBAR_ADDR_Msk)
           |  MPU_RBAR_VALID_Msk
           | (region_num & MPU_RBAR_REGION_Msk);
    // RASR: увімкнути | (size-1)<<SIZE | права AP | (не викон. коли !exec)
    r.rasr = MPU_RASR_ENABLE_Msk
           | ((size_pow2 - 1) << MPU_RASR_SIZE_Pos)
           | (ap << MPU_RASR_AP_Pos)
           | (exec ? 0 : MPU_RASR_XN_Msk);
    return r;
}

#define AP_RW_RW  0x3u   // обом режимам: читати й писати
#define AP_RW_RO  0x2u   // привіл. — чит/зап, непривіл. — тільки читати
#define AP_NONE   0x0u   // доступ заборонено обом (для «канарки»)

// Створити задачу: віддати їй власний стек і блок даних.
static void task_create(TCB *t, uint32_t stack_base, uint32_t stack_pow2,
                        uint32_t data_base, uint32_t data_pow2)
{
    // Область 5 — стек задачі: обом чит/зап, виконувати ЗАБОРОНЕНО (XN)
    t->regions[0] = make_region(5, stack_base, stack_pow2, AP_RW_RW, 0);
    // Область 6 — дані задачі: обом чит/зап, теж XN (дані не виконують)
    t->regions[1] = make_region(6, data_base,  data_pow2,  AP_RW_RW, 0);
    // Область 7 — приклад: шматок даних тільки для читання (спільні константи)
    t->regions[2] = make_region(7, data_base,  data_pow2 - 1, AP_RW_RO, 0);

    // указник стека кладемо на вершину стека (стек росте вниз)
    t->sp = (uint32_t *)(stack_base + (1u << stack_pow2));
}
