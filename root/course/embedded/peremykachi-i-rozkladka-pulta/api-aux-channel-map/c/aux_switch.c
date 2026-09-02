#include "aux_switch.h"

#include <stddef.h>

void switch_init(switch_state_t *sw, switch_position_t initial)
{
    if (sw == NULL) {
        return;
    }
    sw->position    = initial;
    sw->transitions = 0U;
}

static switch_position_t switch_commit(switch_state_t *sw, switch_position_t next)
{
    if (next != sw->position) {
        sw->position = next;
        sw->transitions++;
    }
    return sw->position;
}

switch_position_t switch2_update(switch_state_t *sw, uint16_t us)
{
    if (sw == NULL) {
        return SWITCH_POS_LOW;
    }
    /* Смуга 1350..1650 нічого не змінює — саме вона гасить брязкіт тумблера */
    if (sw->position == SWITCH_POS_LOW) {
        if (us > SWITCH_RISE_US) {
            return switch_commit(sw, SWITCH_POS_HIGH);
        }
    } else if (us < SWITCH_FALL_US) {
        return switch_commit(sw, SWITCH_POS_LOW);
    }
    return sw->position;
}

switch_position_t switch3_update(switch_state_t *sw, uint16_t us)
{
    if (sw == NULL) {
        return SWITCH_POS_LOW;
    }
    if (us <= SWITCH3_LOW_HI_US) {
        return switch_commit(sw, SWITCH_POS_LOW);
    }
    if (us >= SWITCH3_CENTER_LO_US && us <= SWITCH3_CENTER_HI_US) {
        return switch_commit(sw, SWITCH_POS_CENTER);
    }
    if (us >= SWITCH3_HIGH_LO_US) {
        return switch_commit(sw, SWITCH_POS_HIGH);
    }
    /* Проміжок між вікнами — тримаємо попередню позицію */
    return sw->position;
}

const char *switch_position_name(switch_position_t pos)
{
    switch (pos) {
    case SWITCH_POS_LOW:    return "нижня";
    case SWITCH_POS_CENTER: return "центральна";
    case SWITCH_POS_HIGH:   return "верхня";
    default:                return "?";
    }
}

typedef struct {
    uint16_t lo_us;
    uint16_t hi_us;
    uint16_t nominal_us;
    const char *name;
    bool needs_gnss;
} mode_window_t;

static const mode_window_t k_mode_windows[FLIGHT_MODE_COUNT] = {
    {  988U, 1230U, 1165U, "STABILIZE", false },
    { 1231U, 1360U, 1295U, "ALT_HOLD",  false },
    { 1361U, 1490U, 1425U, "LOITER",    true  },
    { 1491U, 1620U, 1555U, "AUTO",      true  },
    { 1621U, 1749U, 1685U, "RTL",       true  },
    { 1750U, 2012U, 1815U, "LAND",      false },
};

flight_mode_t flight_mode_from_us(uint16_t us)
{
    for (unsigned i = 0; i < FLIGHT_MODE_COUNT; ++i) {
        if (us <= k_mode_windows[i].hi_us) {
            return (flight_mode_t)i;
        }
    }
    /* Вище за 2012 мкс — остання позиція селектора */
    return FLIGHT_MODE_LAND;
}

uint16_t flight_mode_nominal_us(flight_mode_t mode)
{
    return ((unsigned)mode < FLIGHT_MODE_COUNT) ? k_mode_windows[mode].nominal_us : 1165U;
}

const char *flight_mode_name(flight_mode_t mode)
{
    return ((unsigned)mode < FLIGHT_MODE_COUNT) ? k_mode_windows[mode].name : "?";
}

bool flight_mode_requires_gnss(flight_mode_t mode)
{
    return ((unsigned)mode < FLIGHT_MODE_COUNT) ? k_mode_windows[mode].needs_gnss : false;
}

uint16_t flight_mode_flags(flight_mode_t mode)
{
    return (uint16_t)(1U << (unsigned)mode);
}
