/* flight_recorder.h — бортовий реєстратор подій (чорна скринька), рівень L1.
 *
 * Кільце 16-байтних двійкових кадрів у секції .noinit оперативної пам'яті:
 * переживає програмне скидання, спрацювання Watchdog і вихід із аварійного
 * обробника, гине лише разом із живленням SRAM. Жодного форматування тексту,
 * жодної купи, запис кадру — константний час і кілька десятків тактів.
 *
 * Усі функції запису безпечні для виклику з переривання: індекс і лічильники
 * рухаються під забороненими перериваннями (PRIMASK), тіло кадру заповнюється
 * вже у зарезервованому слоті.
 */
#ifndef FLIGHT_RECORDER_H
#define FLIGHT_RECORDER_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#define BLACKBOX_MAGIC           0x424F5831u /* 'BOX1' у пам'яті   */
#define BLACKBOX_SCHEMA          1u          /* версія формату кадру */
#define BLACKBOX_CAPACITY        256u        /* 256 · 16 Б = 4 КБ RAM */
#define BLACKBOX_POST_TRIGGER    8u          /* кадрів після тригера, тоді заморозка */
#define BLACKBOX_FRAME_CRC_BYTES 14u         /* CRC кадру рахується над полями 0..13 */
#define BLACKBOX_HEAD_CRC_BYTES  16u         /* CRC заголовка — над magic..crash_count */

typedef enum {
    SUBSYS_CORE   = 0x00, /* ядро, винятки, планувальник */
    SUBSYS_POWER  = 0x01,
    SUBSYS_NAV    = 0x02,
    SUBSYS_MOTORS = 0x03,
    SUBSYS_COM    = 0x04
} SubsystemId_t;

typedef enum {
    EVT_NONE         = 0x00,
    EVT_BOOT         = 0x01, /* старт прошивки, у payload — причина скидання */
    EVT_STATE_CHANGE = 0x02,
    EVT_BUS_ERROR    = 0x03,
    EVT_WARN_THRESH  = 0x04,
    EVT_HEARTBEAT    = 0x05, /* періодичний зріз здоров'я, раз на 1–2 с */
    EVT_LINK_STATS   = 0x06,
    EVT_CRASH_PANIC  = 0xFF
} EventId_t;

/* --- кадр: рівно 16 байтів, вирівняних на 4 --------------------------------
 * aligned(4) обов'язкове: на Cortex-M0+ і RISC-V без непарного доступу читання
 * timestamp_ms за адресою, не кратною чотирьом, дає апаратний виняток.
 */
typedef struct __attribute__((packed, aligned(4))) {
    uint32_t timestamp_ms;  /* монотонні мілісекунди від старту ядра    */
    uint8_t  subsystem_id;  /* SubsystemId_t                            */
    uint8_t  event_id;      /* EventId_t                                */
    uint16_t fsm_state;     /* молодший байт — стан автомата, старший — прапорці ліній */
    uint8_t  payload[6];    /* одна з інтерпретацій BlackBoxPayload_t    */
    uint16_t crc16;         /* CRC-16/CCITT над першими 14 байтами      */
} BlackBoxEvent_t;

_Static_assert(sizeof(BlackBoxEvent_t) == 16, "кадр мусить бути рівно 16 байтів");

/* --- інтерпретації шести байтів корисного навантаження ---------------------
 * packed тут не косметика: без нього uint32_t + uint16_t роздувається до
 * восьми байтів вирівнюванням і в кадр більше не влазить.
 */
typedef struct __attribute__((packed)) {
    uint8_t  previous;  /* стан, з якого вийшли  */
    uint8_t  trigger;   /* код події-тригера     */
    uint32_t dwell_ms;  /* скільки пробули в попередньому стані */
} BlackBoxTransition_t;

typedef struct __attribute__((packed)) {
    uint16_t vbat_mv;   /* напруга акумулятора, мВ */
    uint16_t load_ma;   /* струм навантаження, мА  */
    uint16_t code;      /* код помилки шини або порогу */
} BlackBoxHealth_t;

typedef struct __attribute__((packed)) {
    uint32_t pc;        /* адреса інструкції, що впала */
    uint16_t status;    /* молодші 16 бітів CFSR       */
} BlackBoxFault_t;

typedef struct __attribute__((packed)) {
    uint16_t lost_packets;
    int16_t  rssi_dbm;
    int16_t  snr_cb;    /* сотні дБ, щоб лишитися цілим числом */
} BlackBoxLink_t;

typedef union {
    BlackBoxTransition_t transition;
    BlackBoxHealth_t     health;
    BlackBoxFault_t      fault;
    BlackBoxLink_t       link;
    uint8_t              raw[6];
} BlackBoxPayload_t;

_Static_assert(sizeof(BlackBoxTransition_t) == 6, "payload — рівно 6 байтів");
_Static_assert(sizeof(BlackBoxHealth_t) == 6, "payload — рівно 6 байтів");
_Static_assert(sizeof(BlackBoxFault_t) == 6, "payload — рівно 6 байтів");
_Static_assert(sizeof(BlackBoxLink_t) == 6, "payload — рівно 6 байтів");
_Static_assert(sizeof(BlackBoxPayload_t) == 6, "об'єднання не має рости");

/* --- сховище L1 ------------------------------------------------------------
 * Заголовок навмисно розділено на дві частини. Перші 16 байтів (magic..
 * crash_count) міняються рідко — тільки на старті й на аварії, тому їх
 * накриває header_crc. Лічильники нижче міняються на КОЖНОМУ записі; тримати
 * їх під контрольною сумою означало б рахувати CRC заголовка щоразу — це
 * дорожче за сам запис кадру. Їхню осудність перевіряємо діапазоном.
 */
typedef struct __attribute__((aligned(4))) {
    uint32_t magic;
    uint16_t schema;
    uint16_t capacity;
    uint32_t boot_count;
    uint32_t crash_count;
    uint16_t header_crc;        /* CRC-16 над magic..crash_count */
    uint16_t reserved;
    uint32_t sequence;          /* скільки кадрів записано за всю історію */
    uint32_t head;              /* куди ляже наступний кадр */
    uint8_t  frozen;            /* 1 — кільце заморожене, запис відкинуто */
    uint8_t  post_trigger_left; /* скільки кадрів ще пустимо після тригера */
    uint16_t padding;
    BlackBoxEvent_t events[BLACKBOX_CAPACITY];
} BlackBoxStorage_t;

/* Реалізує платформа: монотонний лічильник мілісекунд від старту ядра.
 * Мусить бути читанням лічильника, а не чимось, що блокується. */
extern uint32_t flight_recorder_uptime_ms(void);

/* Викликається один раз якнайраніше в main(), ДО ініціалізації периферії:
 * вирішує, чи вміст .noinit пережив скидання, чи це холодний старт. */
void flight_recorder_init(uint8_t reset_cause);

void flight_recorder_log(SubsystemId_t subsys, EventId_t evt, uint16_t fsm_state,
                         const void *payload, size_t len);

/* Типові події — щоб виклик у прошивці лишався однорядковим. */
void flight_recorder_state(SubsystemId_t subsys, uint8_t previous, uint8_t next,
                           uint8_t hw_flags, uint8_t trigger, uint32_t dwell_ms);
void flight_recorder_health(SubsystemId_t subsys, EventId_t evt, uint16_t fsm_state,
                            uint16_t vbat_mv, uint16_t load_ma, uint16_t code);
void flight_recorder_link(SubsystemId_t subsys, uint16_t lost_packets,
                          int16_t rssi_dbm, int16_t snr_cb);

/* Аварійний слід. Викликається з HardFault_Handler або з обробника PVD. */
void flight_recorder_panic(uint8_t reason, uint32_t pc, uint16_t fault_status);

void flight_recorder_freeze(void);  /* спинити кільце негайно (перед скиданням у L2) */
void flight_recorder_release(void); /* звіт віддано — знову писати */

bool flight_recorder_history_valid(void);  /* передісторія пережила скидання */
bool flight_recorder_crash_pending(void);  /* є незвітований аварійний знімок */

/* Обхід кільця в хронологічному порядку: від найстарішого вцілілого кадру до
 * найновішого. crc_ok = false означає недозаписаний або спотворений кадр —
 * його показують із позначкою, а не мовчки викидають. */
typedef void (*BlackBoxVisitor_t)(const BlackBoxEvent_t *ev, bool crc_ok, void *ctx);
size_t flight_recorder_replay(BlackBoxVisitor_t visit, void *ctx);

/* Суцільний блок для скидання у FRAM/Flash одним потоком SPI. */
const BlackBoxStorage_t *flight_recorder_storage(void);

static inline BlackBoxPayload_t blackbox_payload(const BlackBoxEvent_t *ev)
{
    BlackBoxPayload_t p;
    memcpy(p.raw, ev->payload, sizeof p.raw);
    return p;
}

#endif /* FLIGHT_RECORDER_H */
