#ifndef SIM_DEVICE_H
#define SIM_DEVICE_H

#include <stdbool.h>
#include <stdint.h>

/* Модель давача на шині: реалізує контракт platform.h і дозволяє вносити
   ті самі несправності, які на стенді вносять руками — зняттям живлення,
   повільним наростанням V_DD, забороненою конфігурацією в таблиці. */

typedef struct {
    uint32_t power_off_at_ms; /* мить, коли зникає живлення (NEVER — не зникає) */
    uint32_t power_on_at_ms;  /* мить, коли воно повертається */
    uint32_t por_ramp_ms;     /* час наростання V_DD: до нього чип німий */
} sim_faults_t;

#define SIM_NEVER (0xFFFFFFFFU)

sim_faults_t sim_faults_default(void);

/* Подати живлення й почати віртуальний час із нуля. */
void sim_device_reset(const sim_faults_t *faults);

/* Просунути віртуальний час на 1 мс і застосувати заплановані події. */
void sim_tick(void);

uint32_t sim_now(void);
unsigned sim_recoveries(void); /* скільки разів драйвер рятував шину */
bool sim_sda_stuck(void);

#endif /* SIM_DEVICE_H */
