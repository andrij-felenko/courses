/* ==========================================================================
 *  mag_cal_telemetry.h — трансляція ходу калібрування на наземну станцію
 *  повідомленнями MAVLink MAG_CAL_PROGRESS (#191) і MAG_CAL_REPORT (#192).
 *
 *  Заголовки MAVLink живуть тільки в .c: решта конвеєра не мусить залежати
 *  від згенерованого коду протоколу.
 * ========================================================================== */
#ifndef MAG_CAL_TELEMETRY_H
#define MAG_CAL_TELEMETRY_H

#include "mag_cal_collector.h"
#include "mag_cal_types.h"

/* Стан процедури в термінах, зрозумілих наземній станції. Значення
 * перекладаються в enum MAG_CAL_STATUS усередині mag_cal_telemetry.c. */
typedef enum {
    MAG_CAL_TM_NOT_STARTED = 0,
    MAG_CAL_TM_WAITING,
    MAG_CAL_TM_COLLECTING,
    MAG_CAL_TM_SOLVING,
    MAG_CAL_TM_SUCCESS,
    MAG_CAL_TM_FAILED,
    MAG_CAL_TM_BAD_RADIUS
} mag_cal_tm_status_t;

typedef struct {
    uint8_t  system_id;
    uint8_t  component_id;
    uint8_t  compass_id;
    uint8_t  attempt;             /* номер спроби калібрування від старту плати */
    uint32_t last_progress_ms;    /* обмежувач частоти: не частіше 5 Гц */
} mag_cal_telemetry_t;

void mag_cal_telemetry_init(mag_cal_telemetry_t *tm, uint8_t system_id,
                            uint8_t component_id, uint8_t compass_id);

void mag_cal_telemetry_next_attempt(mag_cal_telemetry_t *tm);

/* Прогрес: маска заповнених секторів і напрямок, у який просимо довернути
 * апарат. Повертає true, коли пакет справді пішов у канал. */
bool mag_cal_telemetry_progress(mag_cal_telemetry_t *tm,
                                const mag_cal_collector_t *col,
                                mag_cal_tm_status_t status,
                                uint32_t now_ms);

/* Підсумок: надсилається один раз після роботи розв'язувача */
void mag_cal_telemetry_report(mag_cal_telemetry_t *tm,
                              const mag_cal_result_t *cal,
                              bool success, bool autosaved);

/* --- Порт плати: віддає готовий кадр у телеметричний канал (радіомодем,
 *     USB-CDC, UDP). Черга й пріоритети — турбота транспорту, не наша. --- */
bool mag_cal_link_write(const uint8_t *frame, uint16_t len);

#endif /* MAG_CAL_TELEMETRY_H */
