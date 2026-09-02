#ifndef FS_STATUS_H
#define FS_STATUS_H

/* Статусний інтерфейс підсистеми: маска відмов, дія арбітра,
 * кадр FAILSAFE_STATUS і текстові сповіщення STATUSTEXT. */

#include "fs_params.h"

/* Бітова маска підтверджених відмов (після відповідних таймерів і гістерезисів). */
#define FS_FAULT_RC_LOST       (1u << 0)
#define FS_FAULT_GCS_LOST      (1u << 1)
#define FS_FAULT_GNSS_HDOP     (1u << 2)
#define FS_FAULT_GNSS_LOST     (1u << 3)
#define FS_FAULT_EKF_DIVERGED  (1u << 4)
#define FS_FAULT_BATT_LOW      (1u << 5)
#define FS_FAULT_BATT_CRIT     (1u << 6)
#define FS_FAULT_FENCE_RADIUS  (1u << 7)
#define FS_FAULT_FENCE_ALT     (1u << 8)
#define FS_FAULT_ESC_FAIL      (1u << 9)
#define FS_FAULT_ATTITUDE_LOST (1u << 10)
#define FS_FAULT_ALL           0x000007FFu

/* Дії впорядковані за суворістю: більший код перекриває менший. */
#define FS_ACTION_NONE      0u
#define FS_ACTION_WARN      1u
#define FS_ACTION_ALTHOLD   2u
#define FS_ACTION_RTL       3u
#define FS_ACTION_LAND      4u
#define FS_ACTION_TERMINATE 5u

/* Правило, що згенерувало дію (поле executing_arbiter кадру). */
#define FS_ARB_NONE       0u
#define FS_ARB_RC_LINK    1u
#define FS_ARB_GCS        2u
#define FS_ARB_NAV        3u
#define FS_ARB_BATT       4u
#define FS_ARB_FENCE      5u
#define FS_ARB_PROPULSION 6u

/* Шкала MAV_SEVERITY. */
#define FS_SEV_EMERGENCY 0u
#define FS_SEV_ALERT     1u
#define FS_SEV_CRITICAL  2u
#define FS_SEV_ERROR     3u
#define FS_SEV_WARNING   4u
#define FS_SEV_NOTICE    5u
#define FS_SEV_INFO      6u

typedef struct {
    uint64_t timestamp_us;        /* Час польотного контролера (мікросекунди) */
    uint32_t active_faults_mask;  /* Бітова маска поточних підтверджених відмов */
    uint8_t  active_action;       /* Поточний аварійний режим (FS_ACTION_*) */
    uint8_t  executing_arbiter;   /* Ідентифікатор правила, що згенерувало дію */
    uint16_t rc_valid_frames_sec; /* Лічильник валідних RC-пакетів за останню секунду */
    float    gnss_hdop;           /* Поточний HDOP супутникового приймача */
    float    batt_cell_min_v;     /* Мінімальна напруга серед усіх комірок батареї */
    float    distance_to_fence_m; /* Відстань до найближчого кордону геозони */
} failsafe_telemetry_t;

#define FS_FRAME_LEN 28u

typedef struct {
    uint8_t action;
    uint8_t arbiter;
} fs_decision_t;

/* Дія одного правила з урахуванням конфігурації та решти активних відмов. */
uint8_t       fs_action_for(uint32_t fault_bit, uint32_t faults,
                            const fs_param_block_t *p, uint8_t *arbiter_out);
/* Арбітраж: найсуворіша дія серед усіх активних відмов. */
fs_decision_t fs_decide(uint32_t faults, const fs_param_block_t *p);
/* Деградація дії, коли її неможливо виконати наявними давачами. */
uint8_t       fs_degrade(uint8_t action, uint32_t faults);

uint8_t fs_severity_of(uint32_t fault_bit);

/* Пакування кадру у прямому порядку байтів. Повертає довжину (0 — замалий буфер). */
uint32_t fs_frame_pack(const failsafe_telemetry_t *t, uint8_t *buf, uint32_t buf_sz);
bool     fs_frame_unpack(const uint8_t *buf, uint32_t len, failsafe_telemetry_t *out);

/* Текст STATUSTEXT для однієї відмови; повертає код важливості MAV_SEVERITY. */
uint8_t fs_statustext(uint32_t fault_bit, const uint32_t faults, const fs_param_block_t *p,
                      const failsafe_telemetry_t *t, char *out, uint32_t sz);
uint8_t fs_statustext_recovered(const fs_param_block_t *p, char *out, uint32_t sz);

const char *fs_action_name(uint8_t action);
const char *fs_arbiter_name(uint8_t arbiter);
const char *fs_fault_name(uint32_t fault_bit);
const char *fs_severity_name(uint8_t sev);

#endif /* FS_STATUS_H */
