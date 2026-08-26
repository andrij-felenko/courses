# ⚙️ Відмовостійкий менеджер конфігурації з випробувальним режимом

Цей практичний модуль демонструє повну інженерну реалізацію конфігураційного рушія для вбудованих систем із захистом від фатальних мережевих збоїв, механізмом випробувального режиму (Trial Run) на 60 секунд, автоматичним відкатом (Safe Rollback), атомарним дводіапазонним збереженням у Flash (Ping-Pong Slots) та покроковою міграцією версій схеми між оновленнями прошивки.

---

### Архітектура та життєвий цикл конфігурації

У реальних проєктах розподілених приладів зміна налаштувань є однією з найризикованіших операцій. Якщо пристрій під час польової експлуатації отримає некоректний порт MQTT-брокера, помилковий ключ шифрування або нульовий інтервал сторожового таймера, він миттєво втратить зв'язок і перетвориться на «цеглину». Повернення такого вузла до життя вимагає фізичного виїзду сервісної бригади, розкриття герметичного корпусу та підключення програматора через інтерфейс SWD/JTAG.

Щоб унеможливити подібні аварії, представлений конфігураційний менеджер реалізує три фундаментальні принципи надійності:

1. **Ізоляція кандидата в оперативній пам'яті (Staging & Trial Run)**. Нова конфігурація ніколи не записується в енергонезалежну пам'ять Flash одразу після надходження по мережі. Вона завантажується у випробувальний буфер в оперативній пам'яті (`g_candidate_config`). Мережевий стек тимчасово перемикається на роботу з кандидатом, і запускається зворотний відлік випробувального терміну (60 секунд).
2. **Автентифіковане підтвердження зв'язку (Application-level Confirmation)**. Критерієм успіху випробування є не просто фізичне підняття радіолінка (Wi-Fi Link UP), а повноцінне проходження прикладного сеансу: успішне встановлення TLS-з'єднання, проходження авторизації на MQTT-брокері та отримання відповіді на сервісний пінг (`PINGRESP` або підтвердження підписки `SUBACK`). Лише після цього хмара або внутрішній наглядач викликає функцію `confirm_commit()`.
3. **Атомарне дводіапазонне збереження (Dual-Slot Ping-Pong)**. Фізична пам'ять розбита на два симетричні сектори — Slot A та Slot B. Запис завжди виконується у неактивний сектор із монотонним збільшенням лічильника `sequence_number`. Поки запис нового сектора не завершено і підсумкова контрольна сума CRC-32 не верифікована, старий робочий сектор залишається повністю неушкодженим. Будь-яке аварійне відключення живлення посеред запису гарантовано не знищить налаштування приладу.

---

### Покроковий розбір алгоритму роботи

Розгляньмо, як рушій обробляє чотири ключові життєві сценарії:

#### 1. Холодний старт після виробництва

При першому увімкненні після виходу з конвеєра обидва слоти Flash є стертими (містять `0xFFFFFFFF`) або мають невалідну контрольну суму CRC. Функція `cfg_manager_init()` зчитує структури заголовків `cfg_header_t` обох секторів, виявляє невідповідність магічних байтів `CFG_MAGIC` (`0x43464731`), автоматично завантажує заводський еталонний профіль (`cfg_load_factory_defaults`), розраховує підсумковий CRC-32 над корисним навантаженням і записує його у перший вільний сектор (Slot A) з початковим номером генерації `sequence_number = 1`.

#### 2. Оновлення прошивки з міграцією схеми (OTA Migration)

Припустимо, прилад оновив бінарний файл з версії v1.0 на v2.0 по повітрю (OTA). При старті нова прошивка зчитує заголовок Slot A і бачить `schema_version = 1`. Менеджер не скидає налаштування наосліп, а викликає функцію `cfg_migrate_v1_to_v2()`. Вона переносить наявні облікові дані Wi-Fi та IP-адресу, автоматично додає нові поля (порт брокера 8883, активацію TLS) з безпечними дефолтами і фіксує нову структуру у Slot B з версією схеми 2 та оновленим номером `sequence_number = 2`.

#### 3. Отримання некоректного профілю та автоматичний відкат

Сервер надсилає приладу адресу брокера, на якому ведуться технічні роботи. Менеджер успішно валідує синтаксис структури і запускає випробувальний режим `cfg_start_trial()`. Пристрій намагається підключитися до вказаного сервера протягом 60 секунд. Оскільки відповіді немає, кожну секунду функція `cfg_timer_tick_1hz()` зменшує лічильник випробування. Після закінчення 60 секунд автомат фіксує таймаут, викликає `cfg_rollback()` і негайно повертає робочий активний профіль, відновлюючи зв'язок зі старим сервером.

#### 4. Обробка реляційних конфліктів

Якщо оператор намагається передати конфігурацію, у якій інтервал відправки телеметрії (`report_interval_s = 60`) більший за таймаут розриву з'єднання (`conn_timeout_s = 10`), локальний валідатор `cfg_validate()` виявляє порушення системного правила узгодженості ще до запуску випробування, відхиляє запит і повертає інформативний код помилки, не чіпаючи активний профіль.

#### 5. Потокобезпечність та інтеграція з операційними системами реального часу

У багатозадачних середовищах FreeRTOS або Zephyr функція `cfg_timer_tick_1hz()` викликається з низькопріоритетної системної задачі таймерів (Timer Daemon Task) або апаратного переривання апаратного таймера. Для запобігання стану гонитви (Race Condition) між задачами прийому мережевих команд і системним таймером доступ до структури `g_candidate_config` та перемикання станів автомата захищаються двійковим семафором або м'ютексом. При цьому критичні секції читання активної конфігурації `g_active_config` оптимізовані для роботи без блокувань за рахунок атомарної заміни робочих вказівників.

---

### Реалізація на мовах C та C++

:::tabs
```c
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
```
```cpp
// cfg_manager.hpp & cfg_manager.cpp - Ідіоматичний C++20 модуль
#include <iostream>
#include <array>
#include <string_view>
#include <cstring>
#include <span>
#include <expected>
#include <optional>
#include <algorithm>

namespace embedded::config {

inline constexpr std::uint32_t Magic = 0x43464731U; // "CFG1"
inline constexpr std::uint16_t SchemaV1 = 1;
inline constexpr std::uint16_t SchemaV2 = 2;
inline constexpr std::uint16_t CurrentSchema = SchemaV2;
inline constexpr std::size_t FlashSectorSize = 256;
inline constexpr std::uint32_t DefaultTrialTimeoutSeconds = 60;

enum class Error : std::int8_t {
    ValidationFailed = -1,
    TrialActive      = -2,
    NoTrialToCommit  = -3,
    FlashCorrupted   = -4,
    SchemaMismatch   = -5
};

struct [[gnu::packed]] PayloadV1 {
    char wifi_ssid[32];
    char wifi_pass[32];
    std::uint32_t broker_ip;
    std::uint32_t report_interval_s;
};

struct [[gnu::packed]] PayloadV2 {
    char wifi_ssid[32];
    char wifi_pass[32];
    char broker_host[48];
    std::uint16_t broker_port;
    std::uint16_t tls_enable;
    std::uint32_t report_interval_s;
    std::uint32_t conn_timeout_s;
};

struct [[gnu::packed]] Header {
    std::uint32_t magic;
    std::uint16_t schema_version;
    std::uint16_t flags;
    std::uint32_t sequence_number;
    std::uint16_t payload_len;
    std::uint16_t reserved;
    std::uint32_t crc32;
};

class FaultTolerantConfigManager {
public:
    FaultTolerantConfigManager() noexcept {
        flash_slot_a_.fill(0xFF);
        flash_slot_b_.fill(0xFF);
    }

    std::expected<void, Error> initialize() noexcept {
        const auto* hdr_a = reinterpret_cast<const Header*>(flash_slot_a_.data());
        const auto* hdr_b = reinterpret_cast<const Header*>(flash_slot_b_.data());

        const bool a_valid = is_slot_valid(flash_slot_a_);
        const bool b_valid = is_slot_valid(flash_slot_b_);

        if (!a_valid && !b_valid) {
            load_factory_defaults(active_config_);
            return write_to_flash(active_config_, 1);
        }

        const std::span<const std::uint8_t> chosen =
            (a_valid && b_valid) ? ((hdr_a->sequence_number >= hdr_b->sequence_number) ? flash_slot_a_ : flash_slot_b_)
                                 : (a_valid ? flash_slot_a_ : flash_slot_b_);

        const auto* chosen_hdr = reinterpret_cast<const Header*>(chosen.data());
        active_slot_idx_ = (chosen.data() == flash_slot_a_.data()) ? 0 : 1;
        last_seq_ = chosen_hdr->sequence_number;

        const auto* payload_raw = chosen.data() + sizeof(Header);

        if (chosen_hdr->schema_version == SchemaV1) {
            const auto* v1 = reinterpret_cast<const PayloadV1*>(payload_raw);
            migrate_v1_to_v2(*v1, active_config_);
            return write_to_flash(active_config_, last_seq_ + 1);
        } else if (chosen_hdr->schema_version == CurrentSchema) {
            std::memcpy(&active_config_, payload_raw, sizeof(PayloadV2));
            return {};
        }

        load_factory_defaults(active_config_);
        return write_to_flash(active_config_, last_seq_ + 1);
    }

    std::expected<void, Error> start_trial(const PayloadV2& candidate, std::uint32_t timeout_s = DefaultTrialTimeoutSeconds) noexcept {
        if (trial_running_) {
            return std::unexpected(Error::TrialActive);
        }
        if (!validate(candidate)) {
            return std::unexpected(Error::ValidationFailed);
        }

        candidate_config_ = candidate;
        trial_running_ = true;
        trial_timer_sec_ = timeout_s;
        return {};
    }

    std::expected<void, Error> confirm_commit() noexcept {
        if (!trial_running_) {
            return std::unexpected(Error::NoTrialToCommit);
        }

        active_config_ = candidate_config_;
        trial_running_ = false;
        trial_timer_sec_ = 0;
        return write_to_flash(active_config_, last_seq_ + 1);
    }

    void rollback() noexcept {
        trial_running_ = false;
        trial_timer_sec_ = 0;
    }

    void tick_1hz() noexcept {
        if (trial_running_ && trial_timer_sec_ > 0) {
            --trial_timer_sec_;
            if (trial_timer_sec_ == 0) {
                rollback();
            }
        }
    }

    [[nodiscard]] const PayloadV2& active_config() const noexcept {
        return trial_running_ ? candidate_config_ : active_config_;
    }

    [[nodiscard]] bool is_trial_active() const noexcept { return trial_running_; }

private:
    static constexpr std::uint32_t calculate_crc32(std::span<const std::uint8_t> data) noexcept {
        std::uint32_t crc = 0xFFFFFFFFU;
        for (std::uint8_t byte : data) {
            crc ^= byte;
            for (int bit = 0; bit < 8; ++bit) {
                crc = (crc >> 1) ^ (0xEDB88320U & (-(crc & 1)));
            }
        }
        return ~crc;
    }

    static bool is_slot_valid(std::span<const std::uint8_t> slot) noexcept {
        if (slot.size() < sizeof(Header)) return false;
        const auto* hdr = reinterpret_cast<const Header*>(slot.data());
        if (hdr->magic != Magic || hdr->payload_len > slot.size() - sizeof(Header)) return false;

        const auto payload = slot.subspan(sizeof(Header), hdr->payload_len);
        return calculate_crc32(payload) == hdr->crc32;
    }

    static void load_factory_defaults(PayloadV2& cfg) noexcept {
        std::memset(&cfg, 0, sizeof(PayloadV2));
        std::strncpy(cfg.wifi_ssid, "Factory_AP", sizeof(cfg.wifi_ssid) - 1);
        std::strncpy(cfg.wifi_pass, "SecretPass123", sizeof(cfg.wifi_pass) - 1);
        std::strncpy(cfg.broker_host, "mqtt.iot-cloud.internal", sizeof(cfg.broker_host) - 1);
        cfg.broker_port = 8883;
        cfg.tls_enable = 1;
        cfg.report_interval_s = 60;
        cfg.conn_timeout_s = 180;
    }

    static void migrate_v1_to_v2(const PayloadV1& v1, PayloadV2& v2) noexcept {
        std::memset(&v2, 0, sizeof(PayloadV2));
        std::strncpy(v2.wifi_ssid, v1.wifi_ssid, sizeof(v2.wifi_ssid) - 1);
        std::strncpy(v2.wifi_pass, v1.wifi_pass, sizeof(v2.wifi_pass) - 1);

        const auto* ip = reinterpret_cast<const std::uint8_t*>(&v1.broker_ip);
        std::snprintf(v2.broker_host, sizeof(v2.broker_host), "%u.%u.%u.%u", ip[0], ip[1], ip[2], ip[3]);

        v2.broker_port = 8883;
        v2.tls_enable = 1;
        v2.report_interval_s = (v1.report_interval_s >= 1 && v1.report_interval_s <= 86400) ? v1.report_interval_s : 60;
        v2.conn_timeout_s = v2.report_interval_s * 3;
    }

    static bool validate(const PayloadV2& cfg) noexcept {
        if (std::strlen(cfg.wifi_ssid) == 0 || cfg.broker_port == 0) return false;
        if (cfg.report_interval_s == 0 || cfg.report_interval_s > 86400) return false;
        if (cfg.conn_timeout_s <= cfg.report_interval_s) return false;
        return true;
    }

    std::expected<void, Error> write_to_flash(const PayloadV2& cfg, std::uint32_t seq) noexcept {
        const std::uint8_t target_idx = (active_slot_idx_ == 0) ? 1 : 0;
        auto& target_slot = (target_idx == 0) ? flash_slot_a_ : flash_slot_b_;

        Header hdr{
            .magic = Magic,
            .schema_version = CurrentSchema,
            .flags = 0,
            .sequence_number = seq,
            .payload_len = sizeof(PayloadV2),
            .reserved = 0,
            .crc32 = calculate_crc32(std::span<const std::uint8_t>{
                reinterpret_cast<const std::uint8_t*>(&cfg), sizeof(PayloadV2)})
        };

        target_slot.fill(0xFF);
        std::memcpy(target_slot.data(), &hdr, sizeof(Header));
        std::memcpy(target_slot.data() + sizeof(Header), &cfg, sizeof(PayloadV2));

        active_slot_idx_ = target_idx;
        last_seq_ = seq;
        return {};
    }

    alignas(4) std::array<std::uint8_t, FlashSectorSize> flash_slot_a_;
    alignas(4) std::array<std::uint8_t, FlashSectorSize> flash_slot_b_;
    PayloadV2 active_config_{};
    PayloadV2 candidate_config_{};
    bool trial_running_{false};
    std::uint32_t trial_timer_sec_{0};
    std::uint32_t last_seq_{0};
    std::uint8_t active_slot_idx_{0};
};

} // namespace embedded::config
```
:::

---

### Демонстраційний сценарій відкату та валідації

Для перевірки стійкості коду наведено демонстраційну програму, яка імітує реальні позаштатні ситуації:
1. Спробу запису некоректної конфігурації, де таймаут менший за період відправки повідомлень (відхиляється ще на етапі синтаксичної валідації).
2. Запуск випробування з недосяжною адресою сервера: система чекає 60 секунд тіків таймера і, не отримавши підтвердження, автоматично повертає старий робочий стан.
3. Успішне застосування валідного кандидата з негайною фіксацією у Flash (новий `sequence_number`).

:::tabs
```c
int main(void) {
    printf("=== СТАРТ ТЕСТУВАННЯ ВІДМОВОСТІЙКОГО МЕНЕДЖЕРА КОНФІГУРАЦІЇ ===\n");
    cfg_manager_init();

    /* Спроба 1: Спроба надіслати некоректну конфігурацію (помилка реляційних меж) */
    cfg_payload_v2_t bad_candidate = g_active_config;
    bad_candidate.conn_timeout_s = 10;
    bad_candidate.report_interval_s = 60; /* Помилка: conn_timeout <= report_interval */

    printf("\n--- ТЕСТ 1: Відхилення некоректних залежностей ---\n");
    cfg_start_trial(&bad_candidate);

    /* Спроба 2: Коректний синтаксис, але сервер недосяжний (емуляція втрати зв'язку) */
    cfg_payload_v2_t unreachable_candidate = g_active_config;
    strncpy(unreachable_candidate.broker_host, "broken-server.invalid", sizeof(unreachable_candidate.broker_host) - 1);
    unreachable_candidate.conn_timeout_s = 180;
    unreachable_candidate.report_interval_s = 30;

    printf("\n--- ТЕСТ 2: Випробування кандидата та таймаутний відкат ---\n");
    if (cfg_start_trial(&unreachable_candidate)) {
        printf("Імітація 60 секунд відсутності мережевого handshake...\n");
        for (int sec = 0; sec < 60; ++sec) {
            cfg_timer_tick_1hz();
        }
    }

    /* Спроба 3: Успішне підключення та фіксація */
    cfg_payload_v2_t good_candidate = g_active_config;
    strncpy(good_candidate.broker_host, "prod-mqtt.domain.com", sizeof(good_candidate.broker_host) - 1);
    good_candidate.broker_port = 8883;

    printf("\n--- ТЕСТ 3: Успішний Trial Run та Commit ---\n");
    if (cfg_start_trial(&good_candidate)) {
        printf("Мережевий handshake успішний! Виклик confirm_commit()...\n");
        cfg_confirm_commit();
    }

    printf("\n=== ТЕСТУВАННЯ ЗАВЕРШЕНО УСПІШНО ===\n");
    return 0;
}
```
```cpp
int main() {
    std::cout << "=== СТАРТ ТЕСТУВАННЯ ВІДМОВОСТІЙКОГО МЕНЕДЖЕРА (C++20) ===\n";
    embedded::config::FaultTolerantConfigManager manager;
    auto init_res = manager.initialize();
    if (!init_res) {
        std::cerr << "Помилка ініціалізації!\n";
        return 1;
    }

    // Тест 1: Невалідна конфігурація
    auto bad_candidate = manager.active_config();
    bad_candidate.conn_timeout_s = 10;
    bad_candidate.report_interval_s = 60;
    auto trial1 = manager.start_trial(bad_candidate);
    std::cout << "Тест 1 (Очікується помилка): " << (!trial1 ? "ВІДХИЛЕНО УСПІШНО" : "ЗБІЙ ТЕСТУ") << "\n";

    // Тест 2: Випробування з таймаутом і відкатом
    auto unreachable_candidate = manager.active_config();
    std::strncpy(unreachable_candidate.broker_host, "bad.host", sizeof(unreachable_candidate.broker_host) - 1);
    unreachable_candidate.conn_timeout_s = 180;
    unreachable_candidate.report_interval_s = 30;

    if (manager.start_trial(unreachable_candidate)) {
        std::cout << "Тест 2: Прокручування 60 секунд таймера...\n";
        for (int i = 0; i < 60; ++i) {
            manager.tick_1hz();
        }
        std::cout << "Тест 2 стан після таймауту: "
                  << (!manager.is_trial_active() ? "ВІДКАТ ВИКОНАНО" : "ПОМИЛКА") << "\n";
    }

    // Тест 3: Успішний commit
    auto good_candidate = manager.active_config();
    std::strncpy(good_candidate.broker_host, "prod.broker.io", sizeof(good_candidate.broker_host) - 1);
    if (manager.start_trial(good_candidate)) {
        auto commit_res = manager.confirm_commit();
        std::cout << "Тест 3 (Фіксація): " << (commit_res ? "УСПІХ" : "ЗБІЙ") << "\n";
        std::cout << "Поточний активний брокер: " << manager.active_config().broker_host << "\n";
    }

    return 0;
}
```
:::
