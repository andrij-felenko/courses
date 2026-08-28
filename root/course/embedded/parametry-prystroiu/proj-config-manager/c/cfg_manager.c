/* cfg_manager.c - Відмовостійкий менеджер конфігурації (C99) */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CFG_MAGIC           0x43464731UL /* "CFG1" */
#define CFG_SCHEMA_V1       1U
#define CFG_SCHEMA_V2       2U
#define CURRENT_SCHEMA_VER  CFG_SCHEMA_V2

#define FLASH_SECTOR_SIZE   256U
#define TRIAL_TIMEOUT_SEC   60U

/* Структура конфігурації Схеми v1 (застаріла) */
typedef struct {
    char wifi_ssid[32];
    char wifi_pass[32];
    uint32_t broker_ip;
    uint32_t report_interval_s;
} __attribute__((packed)) cfg_payload_v1_t;

/* Структура конфігурації Схеми v2 (поточна) */
typedef struct {
    char wifi_ssid[32];
    char wifi_pass[32];
    char broker_host[48];
    uint16_t broker_port;
    uint16_t tls_enable;
    uint32_t report_interval_s;
    uint32_t conn_timeout_s;
} __attribute__((packed)) cfg_payload_v2_t;

/* Заголовок сектора Flash */
typedef struct {
    uint32_t magic;
    uint16_t schema_version;
    uint16_t flags;
    uint32_t sequence_number;
    uint16_t payload_len;
    uint16_t reserved;
    uint32_t crc32;
} __attribute__((packed)) cfg_header_t;

/* Апаратна емуляція двох слотів Flash (Ping-Pong) */
static uint8_t flash_slot_a[FLASH_SECTOR_SIZE];
static uint8_t flash_slot_b[FLASH_SECTOR_SIZE];

/* Стан менеджера в RAM */
typedef enum {
    CFG_STATE_ACTIVE = 0,
    CFG_STATE_TRIAL_RUNNING
} cfg_run_state_t;

static cfg_payload_v2_t g_active_config;
static cfg_payload_v2_t g_candidate_config;
static cfg_run_state_t  g_state = CFG_STATE_ACTIVE;
static uint32_t         g_trial_timer_sec = 0;
static uint32_t         g_last_seq = 0;
static uint8_t          g_active_slot_idx = 0; /* 0: Slot A, 1: Slot B */

/* Програмна функція обчислення CRC-32 (IEEE 802.3) */
static uint32_t crc32_calculate(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFUL;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320UL & (-(crc & 1)));
        }
    }
    return ~crc;
}

/* Дефолтна ініціалізація поточної схеми v2 */
static void cfg_load_factory_defaults(cfg_payload_v2_t *cfg) {
    memset(cfg, 0, sizeof(cfg_payload_v2_t));
    strncpy(cfg->wifi_ssid, "Factory_AP", sizeof(cfg->wifi_ssid) - 1);
    strncpy(cfg->wifi_pass, "SecretPass123", sizeof(cfg->wifi_pass) - 1);
    strncpy(cfg->broker_host, "mqtt.iot-cloud.internal", sizeof(cfg->broker_host) - 1);
    cfg->broker_port = 8883;
    cfg->tls_enable = 1;
    cfg->report_interval_s = 60;
    cfg->conn_timeout_s = 180;
}

/* Міграція: конвертація застарілої схеми v1 у v2 */
static bool cfg_migrate_v1_to_v2(const cfg_payload_v1_t *v1, cfg_payload_v2_t *v2) {
    printf("[CFG MIGRATION] Виявлено v1 схему. Виконується міграція до v2...\n");
    memset(v2, 0, sizeof(cfg_payload_v2_t));
    strncpy(v2->wifi_ssid, v1->wifi_ssid, sizeof(v2->wifi_ssid) - 1);
    strncpy(v2->wifi_pass, v1->wifi_pass, sizeof(v2->wifi_pass) - 1);
    
    /* Конвертація IPv4 адреси у рядок */
    uint8_t ip[4];
    memcpy(ip, &v1->broker_ip, 4);
    snprintf(v2->broker_host, sizeof(v2->broker_host), "%u.%u.%u.%u", ip[0], ip[1], ip[2], ip[3]);
    
    /* Додавання нових полів із безпечними типовими значеннями */
    v2->broker_port = 8883;
    v2->tls_enable = 1;
    v2->report_interval_s = (v1->report_interval_s >= 1 && v1->report_interval_s <= 86400) ? v1->report_interval_s : 60;
    v2->conn_timeout_s = v2->report_interval_s * 3;
    return true;
}

/* Локальна валідація схеми v2 */
static bool cfg_validate(const cfg_payload_v2_t *cfg) {
    if (strlen(cfg->wifi_ssid) == 0 || strlen(cfg->wifi_ssid) > 31) {
        printf("[VALIDATION ERROR] Порожній або задовгий SSID\n");
        return false;
    }
    if (cfg->broker_port == 0) {
        printf("[VALIDATION ERROR] Порт брокера не може бути 0\n");
        return false;
    }
    if (cfg->report_interval_s == 0 || cfg->report_interval_s > 86400) {
        printf("[VALIDATION ERROR] Інтервал звітування %u c поза межами [1, 86400]\n", cfg->report_interval_s);
        return false;
    }
    /* Крос-параметрична перевірка: таймаут зв'язку має перевищувати інтервал звітування */
    if (cfg->conn_timeout_s <= cfg->report_interval_s) {
        printf("[VALIDATION ERROR] conn_timeout_s (%u) <= report_interval_s (%u)\n",
               cfg->conn_timeout_s, cfg->report_interval_s);
        return false;
    }
    return true;
}

/* Атомарний запис у вільний сектор Flash */
static bool cfg_write_to_flash(const cfg_payload_v2_t *cfg, uint32_t next_seq) {
    uint8_t target_slot_idx = (g_active_slot_idx == 0) ? 1 : 0;
    uint8_t *target_slot = (target_slot_idx == 0) ? flash_slot_a : flash_slot_b;

    cfg_header_t hdr;
    hdr.magic = CFG_MAGIC;
    hdr.schema_version = CURRENT_SCHEMA_VER;
    hdr.flags = 0;
    hdr.sequence_number = next_seq;
    hdr.payload_len = sizeof(cfg_payload_v2_t);
    hdr.reserved = 0;
    hdr.crc32 = crc32_calculate((const uint8_t*)cfg, sizeof(cfg_payload_v2_t));

    /* Емуляція запису сторінки Flash */
    memset(target_slot, 0xFF, FLASH_SECTOR_SIZE);
    memcpy(target_slot, &hdr, sizeof(cfg_header_t));
    memcpy(target_slot + sizeof(cfg_header_t), cfg, sizeof(cfg_payload_v2_t));

    g_active_slot_idx = target_slot_idx;
    g_last_seq = next_seq;
    printf("[FLASH WRITE] Конфігурацію успішно збережено у Slot %c (Seq: %u, CRC: 0x%08X)\n",
           target_slot_idx ? 'B' : 'A', next_seq, hdr.crc32);
    return true;
}

/* Ініціалізація та пошук валідного слота */
bool cfg_manager_init(void) {
    const cfg_header_t *hdr_a = (const cfg_header_t*)flash_slot_a;
    const cfg_header_t *hdr_b = (const cfg_header_t*)flash_slot_b;

    bool a_valid = (hdr_a->magic == CFG_MAGIC) &&
                   (crc32_calculate(flash_slot_a + sizeof(cfg_header_t), hdr_a->payload_len) == hdr_a->crc32);
    bool b_valid = (hdr_b->magic == CFG_MAGIC) &&
                   (crc32_calculate(flash_slot_b + sizeof(cfg_header_t), hdr_b->payload_len) == hdr_b->crc32);

    if (!a_valid && !b_valid) {
        printf("[CFG INIT] Валідних конфігурацій не знайдено. Застосування Factory Defaults...\n");
        cfg_load_factory_defaults(&g_active_config);
        cfg_write_to_flash(&g_active_config, 1);
        return true;
    }

    /* Вибір слота з найновішою послідовністю (Sequence) */
    const uint8_t *chosen_raw = NULL;
    const cfg_header_t *chosen_hdr = NULL;

    if (a_valid && b_valid) {
        if (hdr_a->sequence_number >= hdr_b->sequence_number) {
            chosen_raw = flash_slot_a;
            chosen_hdr = hdr_a;
            g_active_slot_idx = 0;
        } else {
            chosen_raw = flash_slot_b;
            chosen_hdr = hdr_b;
            g_active_slot_idx = 1;
        }
    } else if (a_valid) {
        chosen_raw = flash_slot_a;
        chosen_hdr = hdr_a;
        g_active_slot_idx = 0;
    } else {
        chosen_raw = flash_slot_b;
        chosen_hdr = hdr_b;
        g_active_slot_idx = 1;
    }

    g_last_seq = chosen_hdr->sequence_number;
    const void *payload_ptr = chosen_raw + sizeof(cfg_header_t);

    /* Перевірка потреби в міграції */
    if (chosen_hdr->schema_version == CFG_SCHEMA_V1) {
        const cfg_payload_v1_t *v1 = (const cfg_payload_v1_t*)payload_ptr;
        cfg_migrate_v1_to_v2(v1, &g_active_config);
        /* Збереження мігрованої структури з оновленою схемою */
        cfg_write_to_flash(&g_active_config, g_last_seq + 1);
    } else if (chosen_hdr->schema_version == CURRENT_SCHEMA_VER) {
        memcpy(&g_active_config, payload_ptr, sizeof(cfg_payload_v2_t));
        printf("[CFG INIT] Успішно завантажено Slot %c (Ver: %u, Seq: %u)\n",
               g_active_slot_idx ? 'B' : 'A', chosen_hdr->schema_version, g_last_seq);
    } else {
        printf("[CFG INIT FATAL] Невідома версія схеми (%u). Відкат до дефолтів.\n", chosen_hdr->schema_version);
        cfg_load_factory_defaults(&g_active_config);
        cfg_write_to_flash(&g_active_config, g_last_seq + 1);
    }

    return true;
}

/* Запуск випробувального режиму (Trial Run) */
bool cfg_start_trial(const cfg_payload_v2_t *candidate) {
    if (g_state == CFG_STATE_TRIAL_RUNNING) {
        printf("[TRIAL ERROR] Випробувальний режим уже активний!\n");
        return false;
    }
    if (!cfg_validate(candidate)) {
        printf("[TRIAL REJECTED] Кандидат не пройшов валідацію. Відхилено.\n");
        return false;
    }

    memcpy(&g_candidate_config, candidate, sizeof(cfg_payload_v2_t));
    g_state = CFG_STATE_TRIAL_RUNNING;
    g_trial_timer_sec = TRIAL_TIMEOUT_SEC;
    printf("[TRIAL STARTED] Застосовано кандидата в RAM. Таймер випробування: %u с\n", TRIAL_TIMEOUT_SEC);
    return true;
}

/* Фіксація конфігурації після підтвердження зв'язку */
bool cfg_confirm_commit(void) {
    if (g_state != CFG_STATE_TRIAL_RUNNING) {
        printf("[COMMIT ERROR] Немає активного випробування для фіксації.\n");
        return false;
    }

    memcpy(&g_active_config, &g_candidate_config, sizeof(cfg_payload_v2_t));
    g_state = CFG_STATE_ACTIVE;
    g_trial_timer_sec = 0;
    cfg_write_to_flash(&g_active_config, g_last_seq + 1);
    printf("[COMMIT SUCCESS] Конфігурація успішно зафіксована як активна!\n");
    return true;
}

/* Аварійний відкат */
void cfg_rollback(void) {
    printf("[ROLLBACK TRIGGERED] Відкат до стабільної робочої конфігурації...\n");
    g_state = CFG_STATE_ACTIVE;
    g_trial_timer_sec = 0;
    printf("[ROLLBACK COMPLETE] Відновлено брокер: %s:%u\n",
           g_active_config.broker_host, g_active_config.broker_port);
}

/* Періодичний тік системного таймера (1 Гц) */
void cfg_timer_tick_1hz(void) {
    if (g_state == CFG_STATE_TRIAL_RUNNING) {
        if (g_trial_timer_sec > 0) {
            g_trial_timer_sec--;
            if (g_trial_timer_sec == 0) {
                printf("[TRIAL TIMEOUT] Час випробування вичерпано без підтвердження зв'язку!\n");
                cfg_rollback();
            }
        }
    }
}
