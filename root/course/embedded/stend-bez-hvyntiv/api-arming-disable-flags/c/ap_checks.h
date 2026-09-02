#ifndef AP_CHECKS_H
#define AP_CHECKS_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

/* ArduPilot тримає перелік передпольотних перевірок в одному
 * цілочисельному параметрі ARMING_CHECK. Номер біта = номер перевірки;
 * біт 0 (значення 1) зветься All і вмикає решту незалежно від них. */
typedef enum {
    AP_CHK_ALL = 0,
    AP_CHK_BAROMETER,
    AP_CHK_COMPASS,
    AP_CHK_GPS,
    AP_CHK_INS,
    AP_CHK_PARAMETERS,
    AP_CHK_RC_CHANNELS,
    AP_CHK_BOARD_VOLTAGE,
    AP_CHK_BATTERY_LEVEL,
    AP_CHK_LOGGING,
    AP_CHK_HARDWARE_SWITCH,
    AP_CHK_GPS_CONFIG,
    AP_CHK_SYSTEM,
    AP_CHK_MISSION,
    AP_CHK_RANGEFINDER,
    AP_CHK_COUNT
} ap_check_t;

#define AP_BIT(chk) ((uint32_t)1u << (unsigned)(chk))

const char *ap_check_name(ap_check_t chk);

/* Текст, який прошивка кладе в STATUSTEXT при відмові цієї перевірки.
 * Формулювання залежать від версії — це зразок для впізнавання. */
const char *ap_check_message(ap_check_t chk);

/* ARMING_CHECK читається зі знаком: −1 у наземній станції означає «усі». */
bool ap_check_enabled(int32_t arming_check, ap_check_t chk);

/* Пакет MAVLink STATUSTEXT (#253): поле text — рівно 50 байтів,
 * і завершального нуля в ньому може не бути. */
#define MAV_STATUSTEXT_LEN 50u

typedef enum {
    MAV_SEVERITY_EMERGENCY = 0,
    MAV_SEVERITY_ALERT,
    MAV_SEVERITY_CRITICAL,
    MAV_SEVERITY_ERROR,
    MAV_SEVERITY_WARNING,
    MAV_SEVERITY_NOTICE,
    MAV_SEVERITY_INFO,
    MAV_SEVERITY_DEBUG
} mav_severity_t;

typedef struct {
    uint8_t severity;
    char text[MAV_STATUSTEXT_LEN];
} mav_statustext_t;

void mav_statustext_print(const mav_statustext_t *msg, FILE *out);

/* Складає звіт: несправні підсистеми, чиї перевірки увімкнені в ARMING_CHECK.
 * Записує щонайбільше cap повідомлень, повертає скільки їх потрібно всього. */
size_t ap_prearm_report(int32_t arming_check, uint32_t failed_mask,
                        mav_statustext_t *out, size_t cap);

#endif /* AP_CHECKS_H */
