#ifndef FAILSAFE_H
#define FAILSAFE_H

#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>

/* ---------------------------------------------------------------------
 * Бітова маска стану підсистем.
 *
 * Нуль у біті — норма, одиниця — аномалія відповідного каналу. Номер біта
 * водночас є індексом у таблицях таймерів, тому спершу оголошуємо індекси,
 * а маски виводимо з них: інакше довелося б тримати два незалежні списки,
 * які рано чи пізно розійдуться.
 * ------------------------------------------------------------------- */
enum {
    FS_BIT_RC_LOST = 0,   /* Втрата сигналу пульта керування            */
    FS_BIT_GCS_LOST,      /* Втрата телеметрії наземної станції         */
    FS_BIT_GNSS_GLITCH,   /* Стрибок HDOP / втрата 3D Fix               */
    FS_BIT_BATT_LOW,      /* Перший поріг розряду (попередження)        */
    FS_BIT_BATT_CRIT,     /* Критичний поріг розряду                    */
    FS_BIT_GEOFENCE,      /* Вихід за межі дозволеного радіуса чи стелі */
    FS_BIT_ACTUATOR,      /* Відмова мотора, ESC або сервоприводу       */
    FS_BIT_ATTITUDE_LOSS, /* Втрата розрахунку просторової орієнтації   */
    FS_FAULT_COUNT
};

#define FS_FAULT_RC_LOST       (1u << FS_BIT_RC_LOST)
#define FS_FAULT_GCS_LOST      (1u << FS_BIT_GCS_LOST)
#define FS_FAULT_GNSS_GLITCH   (1u << FS_BIT_GNSS_GLITCH)
#define FS_FAULT_BATT_LOW      (1u << FS_BIT_BATT_LOW)
#define FS_FAULT_BATT_CRIT     (1u << FS_BIT_BATT_CRIT)
#define FS_FAULT_GEOFENCE      (1u << FS_BIT_GEOFENCE)
#define FS_FAULT_ACTUATOR      (1u << FS_BIT_ACTUATOR)
#define FS_FAULT_ATTITUDE_LOSS (1u << FS_BIT_ATTITUDE_LOSS)

#define FS_FAULT_ALL           ((1u << FS_FAULT_COUNT) - 1u)

/* Дії ранжовані за суворістю: більше значення — жорсткіше обмеження
 * польоту. Порядок значень несе сенс, на ньому тримається заборона
 * самовільного пом'якшення (див. fs_arbiter_update). */
typedef enum {
    FS_ACTION_NONE = 0,   /* Штатний політ за командою оператора        */
    FS_ACTION_WARN,       /* Тільки індикація, режим не змінюємо        */
    FS_ACTION_ALTHOLD,    /* Утримання висоти за барометром             */
    FS_ACTION_RTL,        /* Автономне повернення на точку старту       */
    FS_ACTION_LAND,       /* Контрольований спуск на поточному місці    */
    FS_ACTION_TERMINATE   /* Відсікання приводів або парашут            */
} fs_action_t;

const char *fs_action_name(fs_action_t action);
const char *fs_fault_name(unsigned bit);

/* Пороги підтвердження відмови, індексовані номером біта. Нуль означає
 * підтвердження в тому ж такті — так поводяться відмова приводу й втрата
 * орієнтації: фільтрувати їх немає чого, це вже не завада. */
typedef struct {
    uint32_t debounce_ms[FS_FAULT_COUNT];
    uint32_t action_hold_ms; /* мінімальний квант між змінами дії */
} fs_config_t;

fs_config_t fs_config_default(void);

/* ---------------------------------------------------------------------
 * Поштова скринька драйверів.
 *
 * Прапорці ставлять обробники переривань UART/SPI та задача EKF, а читає
 * їх задача арбітра. Тому маска — атомарне слово: жодних read-modify-write
 * без блокування, жодного м'ютекса в ISR.
 * ------------------------------------------------------------------- */
typedef struct {
    _Atomic uint32_t bits;
} fs_inbox_t;

void     fs_inbox_init(fs_inbox_t *box);
void     fs_report_fault(fs_inbox_t *box, uint32_t flags, bool active);
uint32_t fs_inbox_snapshot(const fs_inbox_t *box);

/* Стан арбітра. Прихованого стану, окрім таймерів і зафіксованої дії,
 * немає — саме тому модуль піддається вичерпному тестуванню. */
typedef struct {
    fs_config_t cfg;
    uint32_t    start_ms[FS_FAULT_COUNT]; /* мітка початку аномалії */
    bool        running[FS_FAULT_COUNT];  /* таймер біжить (нуль часу — валідна мітка) */
    uint32_t    confirmed;                /* маска підтверджених відмов */
    fs_action_t action;                   /* видана назовні дія */
    uint32_t    action_since_ms;
    bool        armed;                    /* калібрування завершено */
} fs_state_t;

void fs_arbiter_init(fs_state_t *st, const fs_config_t *cfg);

/* Калібрування сенсорів завершене — з цієї миті арбітр рахує таймери.
 * До виклику він мовчить, інакше кожен старт блокувався б відмовою GNSS,
 * якого просто ще не встигли зловити. */
void fs_arbiter_preflight_done(fs_state_t *st, uint32_t now_ms);

/* Зняття з охорони: повне скидання, включно з фіксацією дії. */
void fs_arbiter_disarm(fs_state_t *st);

/* Явна команда оператора з пульта: зняти фіксацію аварійної дії.
 * Повертає false, якщо виходу немає (термінація в польоті не скасовується). */
bool fs_arbiter_operator_ack(fs_state_t *st, uint32_t now_ms);

/* Один такт арбітражу: знімок сирих прапорців → підтверджена маска → дія. */
fs_action_t fs_arbiter_update(fs_state_t *st, uint32_t raw_faults, uint32_t now_ms);

/* Чиста функція таблиці пріоритетів: маска підтверджених відмов → дія.
 * Без стану, без часу — на ній тримається матричний тест. */
fs_action_t fs_matrix_action(uint32_t confirmed_faults);

uint32_t    fs_arbiter_confirmed(const fs_state_t *st);
fs_action_t fs_arbiter_action(const fs_state_t *st);

#endif /* FAILSAFE_H */
