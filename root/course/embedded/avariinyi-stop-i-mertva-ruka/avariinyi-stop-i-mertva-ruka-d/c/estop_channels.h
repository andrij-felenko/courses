#ifndef ESTOP_CHANNELS_H
#define ESTOP_CHANNELS_H

/* Двоканальний контур аварійного стопу: імпульсна діагностика ліній,
   фільтр брязкоту контактів і контроль часу дискордансу. */

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    CH_FAULT_NONE = 0,
    CH_FAULT_SHORT_TO_SUPPLY,  /* лінія притиснута до шини +24 В */
    CH_FAULT_CROSS_CIRCUIT,    /* канал 1 закорочений на канал 2 */
    CH_FAULT_DISCORDANCE       /* канали розійшлися довше за t_disc */
} channel_fault_t;

typedef struct {
    bool     stable;
    bool     candidate;
    uint32_t settle_ms;
} debounced_input_t;

typedef struct {
    debounced_input_t input[2];
    uint32_t          pulse_timer_ms;
    uint32_t          mismatch_ms;
    bool              mismatching;
    channel_fault_t   fault;
} estop_channels_t;

void estop_channels_init(estop_channels_t *c);

/* Один такт нагляду. Повертає true, лише коли обидва канали стабільно
   замкнені й діагностика ліній не знайшла дефекту. */
bool estop_channels_update(estop_channels_t *c, uint32_t dt_ms);

channel_fault_t estop_channels_fault(const estop_channels_t *c);

#endif /* ESTOP_CHANNELS_H */
