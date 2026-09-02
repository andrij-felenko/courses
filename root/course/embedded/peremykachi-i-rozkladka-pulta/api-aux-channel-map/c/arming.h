#ifndef ARMING_H
#define ARMING_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "aux_switch.h"

/* Бітова маска причин блокування запуску двигунів (розділ 7) */
#define ARM_BLOCK_THROTTLE_NOT_ZERO   0x0001U
#define ARM_BLOCK_FAILSAFE_ACTIVE     0x0002U
#define ARM_BLOCK_PREARM_NOT_ENGAGED  0x0004U
#define ARM_BLOCK_SWITCH_ACTIVE_BOOT  0x0008U
#define ARM_BLOCK_CALIBRATING         0x0010U
#define ARM_BLOCK_TILT_ANGLE          0x0020U
#define ARM_BLOCK_NO_COMPASS_LOCK     0x0040U
#define ARM_BLOCK_NO_GNSS_FIX         0x0080U

#define ARM_THROTTLE_MIN_US   1050U   /* вище — газ вважається піднятим */
#define ARM_MAX_TILT_DEG      25.0f
#define ARM_MAX_HDOP          1.5f

typedef struct {
    uint16_t      throttle_us;      /* газ ПІСЛЯ застосування розкладки каналів */
    bool          failsafe_active;
    bool          prearm_engaged;
    bool          arm_switch;       /* поточна позиція тумблера ARM */
    bool          calibrating;
    float         tilt_deg;
    bool          compass_healthy;
    bool          gnss_fix_3d;
    float         hdop;
    flight_mode_t mode;
} arming_inputs_t;

typedef struct {
    bool boot_latch;   /* тумблер стояв в ARM у момент подачі живлення */
    bool armed;
} arming_state_t;

void arming_init(arming_state_t *st, bool arm_switch_at_boot);

/* Рахує маску причин; оновлює захисну засувку boot_latch */
uint16_t arming_evaluate(arming_state_t *st, const arming_inputs_t *in);

/* Повний такт: перевірка + перемикання стану armed. Повертає armed. */
bool arming_update(arming_state_t *st, const arming_inputs_t *in, uint16_t *blocks_out);

const char *arming_flag_name(uint16_t single_bit);
const char *arming_flag_reason(uint16_t single_bit);

/* Рядок у стилі STATUSTEXT MAVLink; повертає кількість причин */
size_t arming_format_reasons(uint16_t mask, char *buf, size_t size);

#endif /* ARMING_H */
