// ── Груба заборона: глушить УСІ переривання, зокрема критичний таймер. ───
// Простий CPSID i. Небезпечний для реального часу:
// на весь час секції наш таймер СЛІПНЕ → межа 50 мс під загрозою.
static inline void enter_critical_all(void) { __disable_irq(); }   // CPSID i
static inline void exit_critical_all(void)  { __enable_irq();  }   // CPSIE i

// ── Вибіркова заборона (ARMv7-M: Cortex-M3/M4/M7) через BASEPRI: ─────────
// глушить лише переривання НИЖЧІ за поріг, а критичний таймер (пріор. 0)
// лишає ПРАЦЮВАТИ. Саме це рятує реальний час.
static inline uint32_t enter_critical_upto(uint32_t prio)
{
    uint32_t prev = __get_BASEPRI();
    __set_BASEPRI(prio << (8 - __NVIC_PRIO_BITS));  // зсув під реальні біти пріоритету
    return prev;
}
static inline void exit_critical(uint32_t prev) { __set_BASEPRI(prev); }
