/* cfg_manager.h — схема параметрів пристрою, коди станів і публічний інтерфейс
   менеджера конфігурації. Розкладка структур зафіксована: вона лежить у Flash,
   і її читає прошивка іншої версії, ніж та, що писала. */
#ifndef CFG_MANAGER_H
#define CFG_MANAGER_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define CFG_MAGIC           0x43464731UL /* "CFG1" — мітка валідного запису */
#define CFG_SCHEMA_V1       1u
#define CFG_SCHEMA_V2       2u
#define CFG_SCHEMA_CURRENT  CFG_SCHEMA_V2

#define CFG_SSID_LEN  32
#define CFG_PASS_LEN  32
#define CFG_HOST_LEN  48

#define CFG_TRIAL_TIMEOUT_S  60u
#define CFG_REPORT_MAX_S     86400u

/* Схема v1 — прошивки до OTA-оновлення: адреса брокера зберігалась як 4 байти IPv4,
   ні порту, ні TLS, ні таймауту зв'язку в ній не було. */
typedef struct __attribute__((packed)) {
    char     wifi_ssid[CFG_SSID_LEN];
    char     wifi_pass[CFG_PASS_LEN];
    uint8_t  broker_ip[4];
    uint32_t report_interval_s;
} cfg_payload_v1_t;

/* Схема v2 — поточна. */
typedef struct __attribute__((packed)) {
    char     wifi_ssid[CFG_SSID_LEN];
    char     wifi_pass[CFG_PASS_LEN];
    char     broker_host[CFG_HOST_LEN];
    uint16_t broker_port;
    uint16_t tls_enable;
    uint32_t report_interval_s;
    uint32_t conn_timeout_s;
} cfg_payload_v2_t;

/* Заголовок запису в секторі. Пишеться ОСТАННІМ: поки магії немає — для читача
   немає й самого запису. */
typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint16_t schema_version;
    uint16_t flags;
    uint32_t sequence_number;
    uint16_t payload_len;
    uint16_t reserved;
    uint32_t crc32;
} cfg_header_t;

_Static_assert(sizeof(cfg_header_t) == 20, "заголовок не мусить діставати вирівнювання");
_Static_assert(sizeof(cfg_payload_v1_t) == 72, "розкладка v1 зафіксована у Flash");
_Static_assert(sizeof(cfg_payload_v2_t) == 124, "розкладка v2 зафіксована у Flash");

typedef enum {
    CFG_OK = 0,
    CFG_ERR_VALIDATION,   /* кандидат порушує правило схеми або міжпольовий зв'язок */
    CFG_ERR_TRIAL_ACTIVE, /* випробування вже триває */
    CFG_ERR_NO_TRIAL,     /* фіксувати нічого */
    CFG_ERR_FLASH         /* сектор не взяв запис або не пройшов звірку читанням */
} cfg_status_t;

const char *cfg_strerror(cfg_status_t st);

/* CRC-32 (IEEE 802.3). Потрібен і менеджерові, і тому, хто готує запис ззовні. */
uint32_t cfg_crc32(const void *data, size_t len);

/* Заводський профіль — те, з чим пристрій виходить з конвеєра. */
void cfg_load_factory_defaults(cfg_payload_v2_t *cfg);

/* Локальна перевірка кандидата. reason (може бути NULL) дістає пояснення для лога. */
bool cfg_validate(const cfg_payload_v2_t *cfg, char *reason, size_t reason_len);

/* Читає обидва сектори, за потреби мігрує схему й піднімає робочий профіль.
   Викликається до старту задач. */
cfg_status_t cfg_manager_init(void);

/* Робочий профіль для мережевого стека: під час випробування це кандидат,
   у звичайному стані — стабільний профіль. Читання без блокувань — вказівник
   міняється атомарно. Вказівник дійсний до наступної фіксації чи відкату. */
const cfg_payload_v2_t *cfg_live(void);

cfg_status_t cfg_start_trial(const cfg_payload_v2_t *candidate);
cfg_status_t cfg_confirm_commit(void);
void cfg_rollback(void);
void cfg_timer_tick_1hz(void);

bool     cfg_trial_active(void);
uint32_t cfg_trial_seconds_left(void);
uint32_t cfg_sequence(void);
uint8_t  cfg_active_slot(void);   /* 0 — Slot A, 1 — Slot B */

#endif /* CFG_MANAGER_H */
