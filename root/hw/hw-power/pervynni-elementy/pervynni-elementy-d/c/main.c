#include <stdint.h>
#include <stdbool.h>

/* Прогнозування клемної напруги первинного елемента під імпульсним струмом */
bool battery_check_pulse_safe(uint16_t ocv_mv, 
                              uint32_t pulse_current_ua, 
                              uint32_t esr_milliohm, 
                              uint16_t uvlo_threshold_mv, 
                              uint16_t *predicted_vterm_mv) {
    /* Омічне просідання: ΔU (мВ) = I (мкА) * ESR (мОм) / 10^6 */
    uint32_t sag_mv = ((uint64_t)pulse_current_ua * esr_milliohm) / 1000000ULL;
    
    if (ocv_mv <= sag_mv) {
        if (predicted_vterm_mv) *predicted_vterm_mv = 0;
        return false;
    }
    
    uint16_t vterm_mv = ocv_mv - (uint16_t)sag_mv;
    if (predicted_vterm_mv) {
        *predicted_vterm_mv = vterm_mv;
    }
    
    /* Безпечно, якщо напруга під навантаженням перевищує поріг UVLO з запасом 100 мВ */
    return (vterm_mv >= (uvlo_threshold_mv + 100));
}
