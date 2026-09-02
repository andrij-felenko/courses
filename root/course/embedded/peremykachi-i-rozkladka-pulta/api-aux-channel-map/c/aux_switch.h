#ifndef AUX_SWITCH_H
#define AUX_SWITCH_H

#include <stdbool.h>
#include <stdint.h>

/* Дискретне декодування допоміжних каналів: 2- і 3-позиційні тумблери
   з гістерезисом та 6-позиційний селектор режимів польоту. */

typedef enum {
    SWITCH_POS_LOW = 0,
    SWITCH_POS_CENTER,
    SWITCH_POS_HIGH
} switch_position_t;

/* Пороги гістерезису з таблиці розділу 5 */
#define SWITCH_RISE_US 1350U   /* нижче -> вище */
#define SWITCH_FALL_US 1650U   /* вище -> нижче */

#define SWITCH3_LOW_HI_US    1300U
#define SWITCH3_CENTER_LO_US 1350U
#define SWITCH3_CENTER_HI_US 1650U
#define SWITCH3_HIGH_LO_US   1700U

typedef struct {
    switch_position_t position;
    uint32_t transitions;   /* лічильник перемикань — видно брязкіт */
} switch_state_t;

void switch_init(switch_state_t *sw, switch_position_t initial);

/* Повертають новий стан; поза вікнами позиція утримується */
switch_position_t switch2_update(switch_state_t *sw, uint16_t us);
switch_position_t switch3_update(switch_state_t *sw, uint16_t us);
const char *switch_position_name(switch_position_t pos);

typedef enum {
    FLIGHT_MODE_STABILIZE = 0,
    FLIGHT_MODE_ALT_HOLD,
    FLIGHT_MODE_LOITER,
    FLIGHT_MODE_AUTO,
    FLIGHT_MODE_RTL,
    FLIGHT_MODE_LAND,
    FLIGHT_MODE_COUNT
} flight_mode_t;

/* Вікна декодування 6-позиційного селектора (FLTMODE_CH) */
flight_mode_t flight_mode_from_us(uint16_t us);
uint16_t      flight_mode_nominal_us(flight_mode_t mode);
const char   *flight_mode_name(flight_mode_t mode);
bool          flight_mode_requires_gnss(flight_mode_t mode);
uint16_t      flight_mode_flags(flight_mode_t mode);

#endif /* AUX_SWITCH_H */
