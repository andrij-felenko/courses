#include "critical_section.h"
#include "core_cm4.h"

/* Максимально допустима тривалість критичної секції (у тактах ядра) */
#define MAX_ALLOWED_CRITICAL_CYCLES  50U

static inline void profile_critical_section(void) {
    /* 1. Ініціалізація DWT лічильника тактів (виконується один раз при старті) */
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;

    uint32_t start_cycles = DWT->CYCCNT;
    
    critical_section_t cs = critical_section_enter();
    
    /* Робота зі спільним ресурсом */
    g_nav_data.latitude += 10;
    
    critical_section_exit(cs);
    
    uint32_t elapsed = DWT->CYCCNT - start_cycles;
    
    if (elapsed > MAX_ALLOWED_CRITICAL_CYCLES) {
        /* Фіксація перевищення бюджету латентності: запис у журнал або breakpoint */
        __BKPT(0);
    }
}
