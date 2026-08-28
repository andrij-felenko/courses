// Заборонити/дозволити переривання таймера на час читання (критична секція).
// __disable_irq()/__enable_irq() — глобально; точніше глушити лише потрібний
// вектор через NVIC, щоб не чіпати решту переривань системи.
static inline uint64_t atomic_load_u64(volatile uint64_t *p)
{
    uint32_t prim = __get_PRIMASK();   // запам'ятати поточний стан масок
    __disable_irq();                   // коротка критична секція
    uint64_t v = *p;                   // 64-біт читання тепер не перерветься
    if (!prim) __enable_irq();         // відновити лише якщо було дозволено
    return v;
}

// Узгоджене читання ПАРИ (N, M) з одного вікна — обидва під одним замком.
static inline void atomic_load_recip(uint32_t *n, uint64_t *m)
{
    uint32_t prim = __get_PRIMASK();
    __disable_irq();
    *n = g_recip_n;
    *m = g_recip_m;
    if (!prim) __enable_irq();
}
