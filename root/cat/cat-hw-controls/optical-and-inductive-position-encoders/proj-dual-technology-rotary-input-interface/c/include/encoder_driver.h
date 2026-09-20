#ifndef ENCODER_DRIVER_H
#define ENCODER_DRIVER_H

#include "encoder_types.h"

// Ініціалізація структури подвійного давача положення штурвала
void yoke_system_init(yoke_position_system_t *sys, uint32_t qei_ppr, float rvdt_sensitivity, float max_diff_deg, uint32_t timeout_ms);

// Обробка сирих відліків QEI (інкремент/декремент імпульсів)
void yoke_update_qei(yoke_position_system_t *sys, int32_t raw_pulses, bool index_pin);

// Обробка даних DMA АЦП індуктивного давача RVDT
void yoke_update_rvdt(yoke_position_system_t *sys, const uint16_t *adc_samples, uint16_t count);

// Циклічна функція крос-моніторингу та верифікації каналів (викликається у кожному циклі ПЛК)
compare_status_t yoke_process_cycle(yoke_position_system_t *sys, uint32_t current_time_ms);

// Скидання аварійної розбіжності після усунення несправності
bool yoke_reset_fault(yoke_position_system_t *sys);

#endif // ENCODER_DRIVER_H
