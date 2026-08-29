/* cfg_manager.c — автомат конфігурації: холодний старт, міграція схеми,
   випробувальний режим із таймаутом, відкат і атомарний запис у Flash. */
#include "cfg_manager.h"
#include "flash_sim.h"

#include <pthread.h>
#include <stdatomic.h>
#include <stdio.h>
#include <string.h>

/* Стабільний профіль і випробувальний буфер — два окремі об'єкти в RAM.
   Мережевий стек читає той, на який показує g_live_config; вказівник міняється
   атомарно, тож читачам не потрібні ані м'ютекс, ані власна копія. */
static cfg_payload_v2_t g_active_config;
static cfg_payload_v2_t g_candidate_config;
static _Atomic(const cfg_payload_v2_t *) g_live_config = &g_active_config;

static bool     g_trial_running = false;
static uint32_t g_trial_left_s  = 0;
static uint32_t g_last_seq      = 0;
static uint8_t  g_active_slot   = 0;   /* 0 — Slot A, 1 — Slot B */

/* Команди приходять із мережевої задачі, тік — із задачі системних таймерів,
   а автомат один. На FreeRTOS замість pthread тут стоїть xSemaphoreCreateMutex()
   і xSemaphoreTake(); суть та сама — стан міняє хтось один. */
static pthread_mutex_t g_lock = PTHREAD_MUTEX_INITIALIZER;

static void cfg_lock(void)   { pthread_mutex_lock(&g_lock); }
static void cfg_unlock(void) { pthread_mutex_unlock(&g_lock); }

const char *cfg_strerror(cfg_status_t st)
{
    switch (st) {
    case CFG_OK:                return "гаразд";
    case CFG_ERR_VALIDATION:    return "кандидат не пройшов валідацію";
    case CFG_ERR_TRIAL_ACTIVE:  return "випробування вже триває";
    case CFG_ERR_NO_TRIAL:      return "немає чого фіксувати";
    case CFG_ERR_FLASH:         return "сектор Flash не прийняв запис";
    default:                    return "невідомий стан";
    }
}

uint32_t cfg_crc32(const void *data, size_t len)
{
    const uint8_t *p = (const uint8_t *)data;
    uint32_t crc = 0xFFFFFFFFu;

    for (size_t i = 0; i < len; ++i) {
        crc ^= p[i];
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc >> 1) ^ (0xEDB88320u & (uint32_t)(-(int32_t)(crc & 1u)));
        }
    }
    return ~crc;
}

/* Копіювання текстового поля між масивами фіксованої довжини: джерело могло
   приїхати з мережі й не мати завершального нуля. */
static void copy_field(char *dst, size_t dst_cap, const char *src, size_t src_cap)
{
    size_t n = 0;
    while (n < src_cap && src[n] != '\0') {
        ++n;
    }
    if (n > dst_cap - 1) {
        n = dst_cap - 1;
    }
    memcpy(dst, src, n);
    memset(dst + n, 0, dst_cap - n);
}

void cfg_load_factory_defaults(cfg_payload_v2_t *cfg)
{
    memset(cfg, 0, sizeof *cfg);
    copy_field(cfg->wifi_ssid,   CFG_SSID_LEN, "Factory_AP",              CFG_SSID_LEN);
    copy_field(cfg->wifi_pass,   CFG_PASS_LEN, "SecretPass123",           CFG_PASS_LEN);
    copy_field(cfg->broker_host, CFG_HOST_LEN, "mqtt.iot-cloud.internal", CFG_HOST_LEN);
    cfg->broker_port      = 8883;
    cfg->tls_enable       = 1;
    cfg->report_interval_s = 60;
    cfg->conn_timeout_s    = 180;
}

#define REASON(...) \
    do { if (reason != NULL && reason_len > 0) { snprintf(reason, reason_len, __VA_ARGS__); } } while (0)

static bool field_terminated(const char *field, size_t cap)
{
    return memchr(field, '\0', cap) != NULL;
}

bool cfg_validate(const cfg_payload_v2_t *cfg, char *reason, size_t reason_len)
{
    REASON("%s", "");

    /* Структура приїхала з мережі або з Flash: рядки можуть бути без нуля,
       і перший же printf по них вийшов би за межі поля. */
    if (!field_terminated(cfg->wifi_ssid, CFG_SSID_LEN) ||
        !field_terminated(cfg->wifi_pass, CFG_PASS_LEN) ||
        !field_terminated(cfg->broker_host, CFG_HOST_LEN)) {
        REASON("текстове поле без завершального нуля");
        return false;
    }
    if (cfg->wifi_ssid[0] == '\0') {
        REASON("порожній SSID");
        return false;
    }
    if (cfg->broker_host[0] == '\0') {
        REASON("порожня адреса брокера");
        return false;
    }
    if (cfg->broker_port == 0) {
        REASON("порт брокера дорівнює 0");
        return false;
    }
    if (cfg->tls_enable > 1) {
        REASON("прапорець TLS має бути 0 або 1, а не %u", cfg->tls_enable);
        return false;
    }
    if (cfg->report_interval_s == 0 || cfg->report_interval_s > CFG_REPORT_MAX_S) {
        REASON("інтервал звітування %u с поза межами [1, %u]",
               cfg->report_interval_s, CFG_REPORT_MAX_S);
        return false;
    }
    /* Міжпольове правило: не можна оголошувати розрив зв'язку раніше, ніж пристрій
       узагалі мав нагоду вийти в ефір із черговим звітом. */
    if (cfg->conn_timeout_s <= cfg->report_interval_s) {
        REASON("таймаут зв'язку %u с не більший за інтервал звітування %u с",
               cfg->conn_timeout_s, cfg->report_interval_s);
        return false;
    }
    return true;
}

/* Крок міграції v1 → v2: переносимо те, що було, і дораховуємо те, чого не було. */
static void cfg_migrate_v1_to_v2(const cfg_payload_v1_t *v1, cfg_payload_v2_t *v2)
{
    memset(v2, 0, sizeof *v2);
    copy_field(v2->wifi_ssid, CFG_SSID_LEN, v1->wifi_ssid, CFG_SSID_LEN);
    copy_field(v2->wifi_pass, CFG_PASS_LEN, v1->wifi_pass, CFG_PASS_LEN);

    /* v1 знала лише IPv4-адресу — розгортаємо її в ім'я хоста нової схеми. */
    snprintf(v2->broker_host, CFG_HOST_LEN, "%u.%u.%u.%u",
             v1->broker_ip[0], v1->broker_ip[1], v1->broker_ip[2], v1->broker_ip[3]);

    /* Нових полів у старому записі немає, з повітря їх не візьмеш —
       ставимо безпечні дефолти, а не нулі. */
    v2->broker_port = 8883;
    v2->tls_enable  = 1;
    v2->report_interval_s = (v1->report_interval_s >= 1 && v1->report_interval_s <= CFG_REPORT_MAX_S)
                            ? v1->report_interval_s : 60;
    v2->conn_timeout_s = v2->report_interval_s * 3;
}

/* Покроковий підйом запису до поточної схеми. Кожне нове покоління додає сюди
   рівно один крок, тому прилад може перестрибнути кілька версій прошивки одразу. */
static bool decode_record(const cfg_header_t *hdr, const uint8_t *payload, cfg_payload_v2_t *out)
{
    uint16_t ver = hdr->schema_version;

    if (ver == CFG_SCHEMA_V1) {
        if (hdr->payload_len != sizeof(cfg_payload_v1_t)) {
            printf("[CFG] Запис схеми v1 має неправильну довжину (%u)\n", hdr->payload_len);
            return false;
        }
        cfg_payload_v1_t v1;
        memcpy(&v1, payload, sizeof v1);
        printf("[CFG] Знайдено схему v1 — виконуємо міграцію до v%u\n", CFG_SCHEMA_CURRENT);
        cfg_migrate_v1_to_v2(&v1, out);
        return true;   /* наступний крок ланцюга (v2 → v3) стане саме тут */
    }
    if (ver == CFG_SCHEMA_CURRENT) {
        if (hdr->payload_len != sizeof(cfg_payload_v2_t)) {
            printf("[CFG] Запис схеми v2 має неправильну довжину (%u)\n", hdr->payload_len);
            return false;
        }
        memcpy(out, payload, sizeof *out);
        return true;
    }

    /* Прошивку відкотили назад, а у Flash уже лежить новіша схема. */
    printf("[CFG] Невідома версія схеми %u — запис не читаємо\n", ver);
    return false;
}

/* Заголовок сектора копіюємо в локальну структуру: сирі байти Flash не мають
   ані гарантованого вирівнювання, ані типу. */
static bool read_header(uint8_t slot, cfg_header_t *hdr)
{
    const uint8_t *raw = flash_map(slot);
    if (raw == NULL) {
        return false;
    }
    memcpy(hdr, raw, sizeof *hdr);

    if (hdr->magic != CFG_MAGIC) {
        return false;               /* сектор стертий або запис не дописано */
    }
    if (hdr->payload_len == 0 || hdr->payload_len > FLASH_SECTOR_SIZE - sizeof *hdr) {
        return false;
    }
    return cfg_crc32(raw + sizeof *hdr, hdr->payload_len) == hdr->crc32;
}

/* Ping-Pong: пишемо завжди в неактивний сектор і лише потім оголошуємо його активним. */
static cfg_status_t write_record(const cfg_payload_v2_t *cfg, uint32_t seq)
{
    const uint8_t target = (uint8_t)(g_active_slot ^ 1u);

    cfg_header_t hdr = {
        .magic           = CFG_MAGIC,
        .schema_version  = CFG_SCHEMA_CURRENT,
        .flags           = 0,
        .sequence_number = seq,
        .payload_len     = (uint16_t)sizeof *cfg,
        .reserved        = 0,
        .crc32           = cfg_crc32(cfg, sizeof *cfg),
    };

    if (!flash_erase(target)) {
        return CFG_ERR_FLASH;
    }
    if (!flash_program(target, sizeof hdr, cfg, sizeof *cfg)) {
        return CFG_ERR_FLASH;
    }
    /* Заголовок — останнім. Обрив живлення до цієї миті лишає сектор без магії,
       тобто невидимим для читача, а старий сектор і далі активний. */
    if (!flash_program(target, 0, &hdr, sizeof hdr)) {
        return CFG_ERR_FLASH;
    }

    /* Звірка читанням: зношений сектор міг не догасити біти. */
    cfg_header_t back;
    if (!read_header(target, &back) || back.crc32 != hdr.crc32 || back.sequence_number != seq) {
        printf("[FLASH] Slot %c не пройшов звірку — активним лишається Slot %c\n",
               target ? 'B' : 'A', g_active_slot ? 'B' : 'A');
        return CFG_ERR_FLASH;
    }

    g_active_slot = target;
    g_last_seq    = seq;
    printf("[FLASH] Записано Slot %c: seq=%u, схема v%u, CRC=0x%08X\n",
           target ? 'B' : 'A', seq, CFG_SCHEMA_CURRENT, hdr.crc32);
    return CFG_OK;
}

cfg_status_t cfg_manager_init(void)
{
    /* Викликається до старту задач: автомата ще ніхто не бачить, блокування зайве. */
    cfg_header_t hdr[FLASH_SLOT_COUNT];
    bool ok[FLASH_SLOT_COUNT];
    uint32_t highest = 0;

    for (uint8_t s = 0; s < FLASH_SLOT_COUNT; ++s) {
        ok[s] = read_header(s, &hdr[s]);
        if (ok[s] && hdr[s].sequence_number > highest) {
            highest = hdr[s].sequence_number;
        }
    }

    /* Спершу найсвіжіше покоління; якщо воно не читається — старіше. */
    uint8_t order[FLASH_SLOT_COUNT];
    uint8_t n = 0;
    if (ok[0] && ok[1]) {
        const bool a_newer = hdr[0].sequence_number >= hdr[1].sequence_number;
        order[0] = a_newer ? 0 : 1;
        order[1] = a_newer ? 1 : 0;
        n = 2;
    } else if (ok[0]) {
        order[0] = 0;
        n = 1;
    } else if (ok[1]) {
        order[0] = 1;
        n = 1;
    }

    char reason[96];
    for (uint8_t i = 0; i < n; ++i) {
        const uint8_t slot = order[i];
        const uint8_t *payload = flash_map(slot) + sizeof(cfg_header_t);

        if (!decode_record(&hdr[slot], payload, &g_active_config)) {
            continue;
        }
        /* Мігрований запис проходить ту саму перевірку, що й кандидат із мережі. */
        if (!cfg_validate(&g_active_config, reason, sizeof reason)) {
            printf("[CFG] Slot %c відкинуто: %s\n", slot ? 'B' : 'A', reason);
            continue;
        }

        g_active_slot   = slot;
        g_last_seq      = hdr[slot].sequence_number;
        g_trial_running = false;
        g_trial_left_s  = 0;
        atomic_store_explicit(&g_live_config, &g_active_config, memory_order_release);
        printf("[CFG] Завантажено Slot %c: схема v%u, seq=%u\n",
               slot ? 'B' : 'A', hdr[slot].schema_version, g_last_seq);

        if (hdr[slot].schema_version != CFG_SCHEMA_CURRENT) {
            /* Мігровану структуру одразу фіксуємо в сусідньому секторі:
               наступний старт уже не мігруватиме. */
            return write_record(&g_active_config, g_last_seq + 1);
        }
        return CFG_OK;
    }

    printf("[CFG] Придатного запису немає — беремо заводський профіль\n");
    cfg_load_factory_defaults(&g_active_config);
    g_trial_running = false;
    g_trial_left_s  = 0;
    atomic_store_explicit(&g_live_config, &g_active_config, memory_order_release);
    g_active_slot = 1;   /* щоб перший запис ліг у Slot A */
    return write_record(&g_active_config, highest + 1);
}

const cfg_payload_v2_t *cfg_live(void)
{
    return atomic_load_explicit(&g_live_config, memory_order_acquire);
}

cfg_status_t cfg_start_trial(const cfg_payload_v2_t *candidate)
{
    char reason[96];
    if (!cfg_validate(candidate, reason, sizeof reason)) {
        printf("[TRIAL] Кандидата відхилено: %s\n", reason);
        return CFG_ERR_VALIDATION;
    }

    cfg_lock();
    if (g_trial_running) {
        cfg_unlock();
        return CFG_ERR_TRIAL_ACTIVE;
    }
    memcpy(&g_candidate_config, candidate, sizeof g_candidate_config);
    /* Стек починає працювати з кандидатом; g_active_config лишається цілим —
       саме тому відкат нічого не відновлює, а лише повертає вказівник. */
    atomic_store_explicit(&g_live_config, &g_candidate_config, memory_order_release);
    g_trial_running = true;
    g_trial_left_s  = CFG_TRIAL_TIMEOUT_S;
    cfg_unlock();

    printf("[TRIAL] Кандидат у роботі (%s:%u), %u с до автоматичного відкату\n",
           candidate->broker_host, candidate->broker_port, CFG_TRIAL_TIMEOUT_S);
    return CFG_OK;
}

static void rollback_locked(void)
{
    atomic_store_explicit(&g_live_config, &g_active_config, memory_order_release);
    g_trial_running = false;
    g_trial_left_s  = 0;
}

cfg_status_t cfg_confirm_commit(void)
{
    cfg_lock();
    if (!g_trial_running) {
        cfg_unlock();
        return CFG_ERR_NO_TRIAL;
    }

    /* Спершу Flash. Якщо сектор не взяв запис — відкочуємось, а не вдаємо успіх:
       інакше після перезавантаження пристрій опинився б на старому профілі,
       думаючи, що працює на новому. */
    const cfg_status_t st = write_record(&g_candidate_config, g_last_seq + 1);
    if (st != CFG_OK) {
        rollback_locked();
        cfg_unlock();
        printf("[COMMIT] Фіксація не вдалася (%s) — повернуто робочий профіль\n", cfg_strerror(st));
        return st;
    }

    /* Читачі поки тримають кандидата, тож копіювати в g_active_config безпечно:
       ніхто не бачить його наполовину переписаним. */
    memcpy(&g_active_config, &g_candidate_config, sizeof g_active_config);
    atomic_store_explicit(&g_live_config, &g_active_config, memory_order_release);
    g_trial_running = false;
    g_trial_left_s  = 0;
    cfg_unlock();

    printf("[COMMIT] Кандидата зафіксовано як активний профіль\n");
    return CFG_OK;
}

void cfg_rollback(void)
{
    cfg_lock();
    const bool was_running = g_trial_running;
    rollback_locked();
    cfg_unlock();

    if (was_running) {
        printf("[ROLLBACK] Повернуто робочий профіль: %s:%u\n",
               g_active_config.broker_host, g_active_config.broker_port);
    }
}

/* Тік із задачі системних таймерів (1 Гц). */
void cfg_timer_tick_1hz(void)
{
    bool timed_out = false;

    cfg_lock();
    if (g_trial_running && g_trial_left_s > 0) {
        if (--g_trial_left_s == 0) {
            rollback_locked();
            timed_out = true;
        }
    }
    cfg_unlock();

    /* Друкуємо поза критичною секцією: лог не має тримати автомат. */
    if (timed_out) {
        printf("[TRIAL] Підтвердження не надійшло — таймаут, відкат виконано\n");
        printf("[ROLLBACK] Повернуто робочий профіль: %s:%u\n",
               g_active_config.broker_host, g_active_config.broker_port);
    }
}

bool cfg_trial_active(void)
{
    cfg_lock();
    const bool running = g_trial_running;
    cfg_unlock();
    return running;
}

uint32_t cfg_trial_seconds_left(void)
{
    cfg_lock();
    const uint32_t left = g_trial_left_s;
    cfg_unlock();
    return left;
}

uint32_t cfg_sequence(void) { return g_last_seq; }
uint8_t  cfg_active_slot(void) { return g_active_slot; }
