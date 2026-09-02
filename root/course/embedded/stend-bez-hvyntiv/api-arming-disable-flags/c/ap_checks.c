#include "ap_checks.h"

#include <string.h>

static const struct {
    const char *name;
    const char *message;
} k_checks[AP_CHK_COUNT] = {
    [AP_CHK_ALL]             = {"All",             ""},
    [AP_CHK_BAROMETER]       = {"Barometer",       "PreArm: Baro not healthy"},
    [AP_CHK_COMPASS]         = {"Compass",         "PreArm: Compass not calibrated"},
    [AP_CHK_GPS]             = {"GPS",             "PreArm: Need 3D Fix"},
    [AP_CHK_INS]             = {"INS",             "PreArm: Accels not calibrated"},
    [AP_CHK_PARAMETERS]      = {"Parameters",      "PreArm: Check FS_THR_VALUE"},
    [AP_CHK_RC_CHANNELS]     = {"RC Channels",     "PreArm: RC not calibrated"},
    [AP_CHK_BOARD_VOLTAGE]   = {"Board Voltage",   "PreArm: Check board voltage"},
    [AP_CHK_BATTERY_LEVEL]   = {"Battery Level",   "PreArm: Battery below minimum arming voltage"},
    [AP_CHK_LOGGING]         = {"Logging",         "PreArm: Logging failed"},
    [AP_CHK_HARDWARE_SWITCH] = {"Hardware Switch", "PreArm: Safety Switch"},
    [AP_CHK_GPS_CONFIG]      = {"GPS Config",      "PreArm: GPS 1 failing configuration checks"},
    [AP_CHK_SYSTEM]          = {"System",          "PreArm: Internal errors detected"},
    [AP_CHK_MISSION]         = {"Mission",         "PreArm: Mission is empty"},
    [AP_CHK_RANGEFINDER]     = {"Rangefinder",     "PreArm: Rangefinder 1: Not Detected"},
};

const char *ap_check_name(ap_check_t chk)
{
    return ((unsigned)chk < AP_CHK_COUNT) ? k_checks[chk].name : "<невідома перевірка>";
}

const char *ap_check_message(ap_check_t chk)
{
    return ((unsigned)chk < AP_CHK_COUNT) ? k_checks[chk].message : "";
}

bool ap_check_enabled(int32_t arming_check, ap_check_t chk)
{
    if ((unsigned)chk >= AP_CHK_COUNT) {
        return false;
    }
    if (arming_check < 0) {
        return true;                       /* наземна станція пише −1 як «усі» */
    }
    if ((arming_check & 1) != 0) {
        return true;                       /* біт All накриває решту */
    }
    return ((arming_check >> (int)chk) & 1) != 0;
}

static void statustext_fill(mav_statustext_t *msg, mav_severity_t severity, const char *text)
{
    memset(msg, 0, sizeof(*msg));
    msg->severity = (uint8_t)severity;
    size_t len = strlen(text);
    if (len > MAV_STATUSTEXT_LEN) {
        len = MAV_STATUSTEXT_LEN;          /* довший текст прошивка просто зрізає */
    }
    memcpy(msg->text, text, len);
}

void mav_statustext_print(const mav_statustext_t *msg, FILE *out)
{
    /* Нуля може не бути — довжину рахуємо самі. */
    size_t len = 0;
    while (len < MAV_STATUSTEXT_LEN && msg->text[len] != '\0') {
        ++len;
    }
    fprintf(out, "    [severity=%u] %.*s\n", msg->severity, (int)len, msg->text);
}

size_t ap_prearm_report(int32_t arming_check, uint32_t failed_mask,
                        mav_statustext_t *out, size_t cap)
{
    size_t needed = 0;

    for (unsigned i = 1; i < AP_CHK_COUNT; ++i) {   /* біт 0 — не підсистема */
        const ap_check_t chk = (ap_check_t)i;
        if ((failed_mask & AP_BIT(chk)) == 0) {
            continue;
        }
        if (!ap_check_enabled(arming_check, chk)) {
            continue;                                /* перевірку вимкнено параметром */
        }
        if (needed < cap) {
            statustext_fill(&out[needed], MAV_SEVERITY_CRITICAL, ap_check_message(chk));
        }
        ++needed;
    }
    return needed;
}
