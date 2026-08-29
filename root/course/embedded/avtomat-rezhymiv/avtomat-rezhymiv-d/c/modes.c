#include "modes.h"

bool fm_mode_valid(fm_mode_t mode)
{
    return mode >= FM_MODE_MANUAL && mode < FM_MODE_COUNT;
}

const char *fm_mode_name(fm_mode_t mode)
{
    /* Порядок рядків повторює порядок enum; вихід за межі — не «забули назву»,
       а сигнал зіпсованого коду режиму в пакеті MAVLink. */
    static const char *const names[FM_MODE_COUNT] = {
        "Manual", "Stabilize", "AltHold",   "PosHold", "Guided",
        "Auto",   "RTL",       "Land",      "EmergLand", "Terminate"
    };
    return fm_mode_valid(mode) ? names[mode] : "Invalid";
}

bool fm_mode_needs_attitude(fm_mode_t mode)
{
    /* Кутове положення потрібне всім, крім чистого Acro (там досить гіроскопа)
       і відсічки, яка вже нічого не стабілізує. */
    return mode != FM_MODE_MANUAL && mode != FM_MODE_TERMINATE;
}

bool fm_mode_needs_altitude(fm_mode_t mode)
{
    switch (mode) {
    case FM_MODE_ALT_HOLD:
    case FM_MODE_POS_HOLD:
    case FM_MODE_GUIDED:
    case FM_MODE_AUTO:
    case FM_MODE_RTL:
    case FM_MODE_LAND:
        return true;
    default:
        return false;
    }
}

bool fm_mode_needs_position(fm_mode_t mode)
{
    switch (mode) {
    case FM_MODE_POS_HOLD:
    case FM_MODE_GUIDED:
    case FM_MODE_AUTO:
    case FM_MODE_RTL:
        return true;
    default:
        return false;
    }
}

bool fm_mode_auto_throttle(fm_mode_t mode)
{
    switch (mode) {
    case FM_MODE_ALT_HOLD:
    case FM_MODE_POS_HOLD:
    case FM_MODE_GUIDED:
    case FM_MODE_AUTO:
    case FM_MODE_RTL:
    case FM_MODE_LAND:
    case FM_MODE_EMERGENCY_LAND:
        return true;
    default:
        return false;
    }
}

bool fm_mode_manual_throttle(fm_mode_t mode)
{
    return mode == FM_MODE_MANUAL || mode == FM_MODE_STABILIZE;
}

bool fm_mode_is_autonomous(fm_mode_t mode)
{
    return mode == FM_MODE_AUTO || mode == FM_MODE_GUIDED;
}

bool fm_mode_is_failsafe(fm_mode_t mode)
{
    switch (mode) {
    case FM_MODE_RTL:
    case FM_MODE_LAND:
    case FM_MODE_EMERGENCY_LAND:
    case FM_MODE_TERMINATE:
        return true;
    default:
        return false;
    }
}

fm_mode_t fm_mode_degrade(fm_mode_t mode)
{
    switch (mode) {
    case FM_MODE_AUTO:
    case FM_MODE_GUIDED:
    case FM_MODE_RTL:
    case FM_MODE_POS_HOLD:
        return FM_MODE_ALT_HOLD;
    case FM_MODE_ALT_HOLD:
    case FM_MODE_LAND:
        return FM_MODE_STABILIZE;
    case FM_MODE_STABILIZE:
        return FM_MODE_MANUAL;
    default:
        /* Ручний режим і аварійні стани нижче не деградують: знімати більше
           нічого, лишається апаратна відсічка. */
        return mode;
    }
}

fm_mode_t fm_mode_best_available(bool attitude_ok, bool altitude_ok, bool position_ok)
{
    if (attitude_ok && altitude_ok && position_ok) {
        return FM_MODE_POS_HOLD;
    }
    if (attitude_ok && altitude_ok) {
        return FM_MODE_ALT_HOLD;
    }
    if (attitude_ok) {
        return FM_MODE_STABILIZE;
    }
    return FM_MODE_MANUAL;
}
