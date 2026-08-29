/* Бортовий арбітр повноважень наземних станцій.
 *
 * Модуль стоїть між парсером кадрів і виконавчими контурами: жоден пакет
 * керування польотом не потрапляє в мікшер, поки арбітр не підтвердив, що
 * саме ця станція зараз тримає токен пілота.
 *
 * Стан один на борт, тому API — без покажчика на контекст: так само його
 * викликають із задач FreeRTOS у прозі (arbiter_process_heartbeat,
 * arbiter_is_flight_command_allowed, arbiter_periodic_tick). */
#ifndef ARB_ARBITER_H
#define ARB_ARBITER_H

#include <stdbool.h>
#include <stdint.h>

#include "stations.h"

/* Оренда токена: не почули heartbeat власника довше — вважаємо звʼязок утраченим. */
#define ARB_HEARTBEAT_TIMEOUT_MS 1000u
/* Скільки в змінного пілота часу на перевірку стіків, поки передача не скасується. */
#define ARB_HANDOVER_TIMEOUT_MS  5000u

/* Мертва зона з гістерезисом: увійти в нейтраль важче, ніж у ній лишитися.
 * 3% від шкали ±1000 на вхід, 4.5% на утримання — цього досить, щоб дрейф
 * потенціометрів (-18…+24 одиниці на бюджетному пульті) не зривав перевірку. */
#define ARB_DEADBAND_ENTER 30
#define ARB_DEADBAND_EXIT  45
/* Стіки мусять простояти в нейтралі стільки, перш ніж борт віддасть токен:
 * одиничний кадр міг бути шумом АЦП. */
#define ARB_NEUTRAL_HOLD_MS 300u
/* Газ не центрується — його звіряють із поточною тягою апарата, інакше в мить
 * передачі мотори стрибнуть. 8% від шкали 0…1000. */
#define ARB_THROTTLE_WINDOW 80

typedef enum {
    STATE_IDLE = 0,           /* токена не тримає ніхто */
    STATE_PILOT_ACTIVE,       /* є власник, оренда свіжа */
    STATE_HANDOVER_WAIT_STICK,/* передача зміни: чекаємо нейтралі в кандидата */
    STATE_LINK_LOST,          /* оренда протермінована, керування заборонено */
    STATE_COMMANDER_LOCKED    /* командир перехопив борт */
} arbiter_state_t;

typedef enum {
    ARB_OK = 0,
    ERR_UNKNOWN_STATION,    /* станції немає в реєстрі або її heartbeat протух */
    ERR_ROLE_DENIED,        /* станція є, але такої ролі за нею не записано */
    ERR_BUSY,               /* токен уже в когось */
    ERR_WRONG_STATE,        /* операція не має сенсу в поточному стані */
    ERR_NOT_OWNER,          /* просить не той, хто має право просити */
    ERR_STICK_NOT_NEUTRAL,  /* крен/тангаж/рискання поза мертвою зоною */
    ERR_STICK_HOLD,         /* нейтраль є, але ще не витримана за часом */
    ERR_THROTTLE_MISMATCH,  /* газ не збігається з поточною тягою */
    ERR_HANDOVER_TIMEOUT,   /* вікно передачі зміни згоріло */
    ERR_LOCKED,             /* борт під командиром */
    ERR_TABLE_FULL          /* реєстр станцій забитий */
} arb_err_t;

typedef struct {
    int16_t roll;     /* -1000 .. +1000 */
    int16_t pitch;    /* -1000 .. +1000 */
    int16_t yaw;      /* -1000 .. +1000 */
    int16_t throttle; /*     0 .. +1000 */
} stick_axes_t;

/* Запис нової сесії — єдине місце, де стан міняється не одним полем.
 * У FreeRTOS його закриває коротка критична секція; на голому залізі
 * підставляють заборону переривань. Тримати м'ютекс тут нічого. */
#ifdef ARB_USE_FREERTOS
#  include "FreeRTOS.h"
#  include "task.h"
#  define ARB_CRITICAL_ENTER() taskENTER_CRITICAL()
#  define ARB_CRITICAL_EXIT()  taskEXIT_CRITICAL()
#else
#  define ARB_CRITICAL_ENTER() ((void)0)
#  define ARB_CRITICAL_EXIT()  ((void)0)
#endif

/* seed бери з реального джерела ентропії (UID кристала, шум АЦП, лічильник
 * тактів на момент старту) — константа зробила б nonce передбачуваним. */
void arbiter_init(uint32_t seed, uint32_t now_ms);

/* Кожен heartbeat від будь-якої станції. Оновлює реєстр і, якщо станція є
 * власником токена, продовжує оренду. Статусів лінка, які станція повідомляє
 * про себе, арбітр не читає взагалі: рішення про звʼязок ухвалює лише
 * бортовий таймер (див. асиметричне зникнення каналу). */
arb_err_t arbiter_process_heartbeat(uint8_t gcs_id, uint8_t roles, uint32_t now_ms);

/* Захопити вільний токен пілота. out_nonce — на пакети керування. */
arb_err_t arbiter_request_pilot_token(uint8_t gcs_id, uint32_t now_ms, uint32_t *out_nonce);

/* Чинний пілот пропонує зміну. Далі кандидат мусить показати нейтраль. */
arb_err_t arbiter_initiate_handover(uint8_t current_pilot_id, uint8_t target_gcs_id, uint32_t now_ms);

/* Кандидат шле положення своїх стіків (десятки разів на секунду).
 * ARB_OK повертається один раз — у мить передачі токена. */
arb_err_t arbiter_confirm_handover_sticks(uint8_t candidate_id, const stick_axes_t *sticks,
                                          uint32_t now_ms, uint32_t *out_nonce);

/* Чинний пілот відмовляється від зміни (або передумав). */
arb_err_t arbiter_cancel_handover(uint8_t requester_id, uint32_t now_ms);

/* Безумовне перехоплення командиром: токен переходить до нього незалежно
 * від стану, старий nonce миттєво стає недійсним. */
arb_err_t arbiter_commander_override(uint8_t commander_id, uint32_t now_ms, uint32_t *out_nonce);

/* Командир віддає борт назад — токен нічий, хтось має його запросити. */
arb_err_t arbiter_release_override(uint8_t commander_id, uint32_t now_ms);

/* Гаряча перевірка на кожен пакет стіків: викликається з високопріоритетної
 * задачі, тому всередині — лише порівняння цілих. */
bool arbiter_is_flight_command_allowed(uint8_t src_gcs_id, uint32_t nonce);

/* Канал корисного навантаження живе окремо від навігації: він не залежить
 * ні від токена пілота, ні від командирського замка. */
bool arbiter_is_payload_command_allowed(uint8_t src_gcs_id, uint32_t now_ms);

/* Поточна тяга апарата з мікшера — ціль, під яку кандидат виставляє газ. */
void arbiter_set_current_thrust(int16_t thrust);

/* Перевірка часу: тільки з таймера або високопріоритетної задачі.
 * Поставиш поруч із записом логів на SD — 150 мс запису дадуть фальшивий
 * тайм-аут оренди й безпідставний перехід у LOITER. */
void arbiter_periodic_tick(uint32_t now_ms);

arbiter_state_t arbiter_state(void);
uint8_t         arbiter_active_pilot(void);
uint32_t        arbiter_current_nonce(void);
const char     *arb_err_str(arb_err_t err);
const char     *arb_state_str(arbiter_state_t st);

#endif /* ARB_ARBITER_H */
