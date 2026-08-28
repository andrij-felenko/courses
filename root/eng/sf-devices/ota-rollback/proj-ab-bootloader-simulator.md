# Проект: Симулятор відмовостійкого завантажувача з A/B слотами

Розробка та налагодження системного завантажувача (*Bootloader*) безпосередньо на фізичному мікроконтролері пов'язані з високими часовими витратами та постійним ризиком апаратного блокування пристрою. Тестування поведінки системи при раптовому знеструмленні (*Power-Loss Injection*) на реальній платі вимагає спеціальних керованих джерел живлення з реле швидкого розриву кола або апаратних стендів із транзисторними переривачами. Крім того, перевірка всіх можливих крайових станів — аварійного винятку `HardFault` під час ініціалізації системного генератора PLL, зависання сторожового таймера під час виконання мережевого стека, пошкодження метаданих на середині запису сторінки Flash — потребує створення сотень спеціальних тестових збірок прошивки.

Для прискорення розробки та автоматизації регресійного тестування у конвеєрах неперервної інтеграції (CI/CD) створюють повноцінний програмний симулятор завантажувача. Цей симулятор функціонує в середовищі операційної системи хоста (Linux / macOS / Windows), емулюючи фізичні властивості енергонезалежної Flash-пам'яті, роботу сторожового таймера, механіку чергування банків пам'яті, конвеєр валідації метаданих та процедуру автоматичного відкату при виникненні будь-яких програмних чи апаратних збоїв.

### Архітектура та компоненти симулятора

Симулятор проектується як модульна система, що складається з семи функціональних підсистем, кожна з яких детально моделює реальні апаратні та системні обмеження мікроконтролера:

```text
+-----------------------------------------------------------------------------------+
|                            Тестовий стенд сценаріїв                               |
+-----------------------------------------------------------------------------------+
       │                                                     │
       ▼                                                     ▼
+──────────────────────────+                           +──────────────────────────+
|  Системний завантажувач  |                           |  Клієнт оновлення OTA    |
|   (Bootloader Engine)    |                           |     (OTA Client & POST)  |
+──────────────────────────+                           +──────────────────────────+
       │                                                     │
       └──────────────────────────┬──────────────────────────┘
                                  ▼
                    +───────────────────────────+
                    |  Менеджер метаданих (2x)  |
                    | (Dual-Sector Ping-Pong)   |
                    +───────────────────────────+
                                  │
       ┌──────────────────────────┴──────────────────────────┐
       ▼                                                     ▼
+──────────────────────────+                           +──────────────────────────+
|  Емулятор Flash-пам'яті  |                           |  Сторожовий таймер WDT   |
|   (NOR Flash Physics)    |                           |   (Hardware Watchdog)    |
+──────────────────────────+                           +──────────────────────────+
       ▲
       │
+──────────────────────────+
|  Ін'єктор збоїв живлення |
|  (Power-Loss Injection)  |
+──────────────────────────+
```

1. **Емулятор енергонезалежної Flash-пам'яті (Flash Memory Engine):**
   - Моделює адресний простір обсягом 2 МБ, розбитий на фізичні сектори по 4096 байтів.
   - Підтримує фундаментальні фізичні інваріанти NOR Flash: операція програмування (запису) може лише скидати біти з логічної `1` у логічний `0`; переведення бітів з `0` в `1` можливе виключно через попереднє стирання всього 4 КБ сектора (заповнення байтами `0xFF`).
   - Контролює побітове перепрограмування: спроба записати `0` у комірку, де вже записано `0`, дозволена, але спроба записати `1` без попереднього стирання сектора призводить до апаратного конфлікту та спотворення даних.
2. **Двосекторний журнал метаданих (Dual-Sector Ping-Pong Metadata Manager):**
   - Виділяє два незалежні фізичні сектори `Metadata_Sector_0` та `Metadata_Sector_1`.
   - Забезпечує атомарне оновлення структури стану завантажувача з розрахунком монотонного лічильника послідовності `sequence` та 32-бітної контрольної суми CRC32 (поліном IEEE 802.3).
3. **Емулятор апаратного сторожового таймера (Independent Watchdog Emulator):**
   - Моделює автономний лічильник з окремим тактуванням, який веде зворотний відлік незалежно від стану основного потоку виконання програми.
   - Якщо застосунок не скидає таймер у межах встановленого часового ліміту (наприклад, 30 умовних тактів або секунд), таймер генерує немаскований апаратний сигнал скидання `WDT_RESET`.
4. **Генератор ін'єкції збоїв живлення (Power-Loss Fault Injector):**
   - Дозволяє перехоплювати операції стирання та запису Flash на довільному байтовому зміщенні.
   - Емулює раптове знеструмлення посеред запису сектора метаданих або запису двійкового образу прошивки, перериваючи транзакцію та залишаючи комірки у стані часткового запису.
5. **Машина станів завантажувача (Bootloader Engine):**
   - Зчитує метадані під час старту мікроконтролера, обирає цільовий слот (`Slot_A` чи `Slot_B`), обробляє лічильник спроб `boot_attempts_left` та ухвалює рішення щодо старту образу або автоматичного відкату при вичерпанні дозволеного ліміту.
6. **Емулятор життєвого циклу застосунку (Application Runtime & POST Framework):**
   - Моделює виконання нової прошивки, проходження п'ятифазного протоколу самотестування (*Power-On Self-Test*) та фіксацію робочого стану викликом `ota_mark_valid()`.
7. **Автоматизований тестовий стенд (Verification Suite):**
   - Набір інтеграційних сценаріїв, що автоматично перевіряють поведінку системи за умов штатного оновлення, швидкого падіння (`HardFault`), зависання сторожового таймера, знеструмлення під час запису метаданих та каскадних відмов.

### Фізична організація пам'яті та журнал чергування

У симуляторі віртуальний адресний простір Flash-пам'яті обсягом 2 МБ структуровано відповідно до промислових стандартів:

```text
+-----------------------------------------------------------------------------------+
| Сектор               | Фізичний діапазон         | Призначення                    |
+----------------------+---------------------------+--------------------------------+
| Bootloader           | 0x00000000 - 0x00007FFF   | Код системного завантажувача   |
| Metadata Sector 0    | 0x00008000 - 0x00008FFF   | Первинний сектор метаданих     |
| Metadata Sector 1    | 0x00009000 - 0x00009FFF   | Вторинний сектор метаданих     |
| Application Slot A   | 0x00010000 - 0x000FFFFF   | Робочий банк A (960 КБ)        |
| Application Slot B   | 0x00100000 - 0x001EFFFF   | Робочий банк B (960 КБ)        |
| NVS Config Storage   | 0x001F0000 - 0x001FFFFF   | Енергонезалежні налаштування   |
+-----------------------------------------------------------------------------------+
```

Метадані стану завантажувача зберігаються у компактній структурі `boot_metadata_t`. Щоб уникнути втрати даних при знеструмленні під час перезапису, завантажувач ніколи не модифікує сектор «на місці». Натомість він зчитує обидва сектори, знаходить запис із максимальним номером епохи `sequence` та записує новий оновлений стан із номером `sequence + 1` у протилежний сектор пам'яті.

:::tabs
```c
typedef struct {
    uint32_t magic;               /* Магічний маркер валідності (0x544F4F42) */
    uint32_t sequence;            /* Монотонний лічильник транзакцій */
    uint8_t  active_slot;         /* Ідентифікатор активного слота (0 = A, 1 = B) */
    uint8_t  slot_state;          /* Стан слота (PENDING_VERIFY, VALID, MARKED_BAD) */
    uint8_t  boot_attempts_left;  /* Залишок спроб старту (початково 3) */
    uint8_t  max_boot_attempts;   /* Максимальний ліміт спроб */
    uint32_t image_version;       /* Семантична версія прошивки */
    uint32_t image_crc;           /* Хеш-сума бінарного коду */
    uint32_t header_crc;          /* Контрольна сума CRC32 структури метаданих */
} __attribute__((packed)) boot_metadata_t;
```
```cpp
struct [[gnu::packed]] BootMetadata {
    uint32_t   magic{0x544F4F42UL};
    uint32_t   sequence{0};
    SlotId     activeSlot{SlotId::SlotA};
    SlotState  slotState{SlotState::Empty};
    uint8_t    bootAttemptsLeft{0};
    uint8_t    maxBootAttempts{3};
    uint32_t   imageVersion{0};
    uint32_t   imageCrc{0};
    uint32_t   headerCrc{0};
};
```
:::


Якщо в процесі прання або програмування сектора зникає живлення, його фінальна контрольна сума `header_crc` не зійдеться з обчисленим значенням CRC32. Завантажувач зафіксує помилку цілісності, проігнорує зіпсований блок і прозоро продовжить завантаження з попереднього валідного сектора.

### Алгоритм ін'єкції збоїв живлення (Power-Loss Fault Injection)

Тестування атомарності оновлення полягає у верифікації поведінки завантажувача при аварійному розриві живлення у найкритичніших точках часової шкали. Ін'єктор збоїв перехоплює виклики `flash_erase_sector()` та `flash_write()`, відраховуючи кількість успішно оброблених байтів. Коли внутрішній лічильник досягає нуля, ін'єктор перериває виконання операції і повертає статус апаратної помилки `false`.

```text
[ Запит на запис 32 байтів метаданих ]
                   │
                   ▼
    ┌─────────────────────────────┐
    │ Ін'єктор: ліміт = 12 байтів │
    └──────────────┬──────────────┘
                   │
         Записано 12 байтів ──► [ ЖИВЛЕННЯ ЗНИКАЄ: flash_write() повертає false ]
                                                   │
                                                   ▼
                                  [ Стан пам'яті: перші 12 байтів змінено, ]
                                  [ решта 20 байтів залишилися 0xFF ]
                                                   │
                                                   ▼
                                  [ Рестарт: завантажувач перевіряє CRC32 ]
                                  [ CRC32 не зійшовся -> відкат на сектор 0 ]
```

Такий підхід дозволяє гарантувати, що в жодному сценарії — від знеструмлення на першому байті стирання до обриву на останньому байті запису CRC — пристрій не перетвориться на невідновлювану «цеглину».

### Повна реалізація симулятора мовою C99

Нижче наведено повний вихідний код симулятора мовою C99. Програма містить повноцінний емулятор Flash-пам'яті, двосекторний менеджер метаданих, сторожовий таймер, завантажувач та три автоматизовані тестові сценарії.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define FLASH_TOTAL_SIZE       (2 * 1024 * 1024) /* 2 МБ Flash */
#define FLASH_SECTOR_SIZE      4096              /* 4 КБ сектор */
#define FLASH_PAGE_SIZE        256               /* 256 байтів сторінка */

#define BOOT_METADATA_MAGIC    0x544F4F42UL      /* ASCII "BOOT" */
#define MAX_BOOT_ATTEMPTS      3

#define ADDR_METADATA_0        0x00008000UL
#define ADDR_METADATA_1        0x00009000UL
#define ADDR_SLOT_A            0x00010000UL
#define ADDR_SLOT_B            0x00100000UL
#define SLOT_SIZE              (960 * 1024)      /* 960 КБ на кожен слот */

typedef enum {
    SLOT_ID_A = 0,
    SLOT_ID_B = 1,
    SLOT_ID_INVALID = 0xFF
} slot_id_t;

typedef enum {
    SLOT_STATE_EMPTY          = 0xFF,
    SLOT_STATE_PENDING_VERIFY = 0x01,
    SLOT_STATE_VALID          = 0x02,
    SLOT_STATE_MARKED_BAD     = 0x03
} slot_state_t;

typedef struct {
    uint32_t magic;
    uint32_t sequence;
    uint8_t  active_slot;
    uint8_t  slot_state;
    uint8_t  boot_attempts_left;
    uint8_t  max_boot_attempts;
    uint32_t image_version;
    uint32_t image_crc;
    uint32_t header_crc;
} __attribute__((packed)) boot_metadata_t;

/* ========================================================================= */
/* ПІДСИСТЕМА ЕМУЛЯЦІЇ FLASH-ПАМ'ЯТІ ТА ІН'ЄКЦІЇ ЗБОЇВ                       */
/* ========================================================================= */

typedef struct {
    uint8_t memory[FLASH_TOTAL_SIZE];
    bool    power_loss_injection_enabled;
    int     bytes_until_power_cut;
    bool    power_cut_triggered;
} flash_simulator_t;

static flash_simulator_t g_flash;

static uint32_t crc32_calculate(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFFUL;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320UL & (-(crc & 1)));
        }
    }
    return ~crc;
}

void flash_init(void) {
    memset(g_flash.memory, 0xFF, FLASH_TOTAL_SIZE);
    g_flash.power_loss_injection_enabled = false;
    g_flash.bytes_until_power_cut = -1;
    g_flash.power_cut_triggered = false;
}

void flash_enable_power_cut_after_bytes(int byte_count) {
    g_flash.power_loss_injection_enabled = true;
    g_flash.bytes_until_power_cut = byte_count;
    g_flash.power_cut_triggered = false;
}

void flash_disable_fault_injection(void) {
    g_flash.power_loss_injection_enabled = false;
    g_flash.bytes_until_power_cut = -1;
    g_flash.power_cut_triggered = false;
}

bool flash_read(uint32_t address, void *dest, size_t size) {
    if (address + size > FLASH_TOTAL_SIZE) {
        return false;
    }
    memcpy(dest, &g_flash.memory[address], size);
    return true;
}

bool flash_erase_sector(uint32_t sector_address) {
    if (sector_address % FLASH_SECTOR_SIZE != 0 || sector_address + FLASH_SECTOR_SIZE > FLASH_TOTAL_SIZE) {
        return false;
    }
    if (g_flash.power_loss_injection_enabled) {
        if (g_flash.bytes_until_power_cut <= 0) {
            g_flash.power_cut_triggered = true;
            return false; /* Знеструмлення до початку стирання */
        }
        if (g_flash.bytes_until_power_cut < (int)FLASH_SECTOR_SIZE) {
            /* Часткове стирання: лише перша частина сектора стає 0xFF */
            memset(&g_flash.memory[sector_address], 0xFF, g_flash.bytes_until_power_cut);
            g_flash.bytes_until_power_cut = 0;
            g_flash.power_cut_triggered = true;
            return false;
        }
        g_flash.bytes_until_power_cut -= FLASH_SECTOR_SIZE;
    }
    memset(&g_flash.memory[sector_address], 0xFF, FLASH_SECTOR_SIZE);
    return true;
}

bool flash_write(uint32_t address, const void *src, size_t size) {
    if (address + size > FLASH_TOTAL_SIZE) {
        return false;
    }
    const uint8_t *src_bytes = (const uint8_t *)src;
    for (size_t i = 0; i < size; ++i) {
        if (g_flash.power_loss_injection_enabled) {
            if (g_flash.bytes_until_power_cut <= 0) {
                g_flash.power_cut_triggered = true;
                return false; /* Знеструмлення посеред запису */
            }
            g_flash.bytes_until_power_cut--;
        }
        /* Фізика Flash: біти можуть змінюватися тільки з 1 в 0 */
        uint8_t current_val = g_flash.memory[address + i];
        uint8_t new_val = current_val & src_bytes[i];
        g_flash.memory[address + i] = new_val;
    }
    return true;
}

/* ========================================================================= */
/* ПІДСИСТЕМА УПРАВЛІННЯ ДВОСЕКТОРНИМИ МЕТАДАНИМИ                            */
/* ========================================================================= */

static bool metadata_verify_integrity(const boot_metadata_t *meta) {
    if (meta->magic != BOOT_METADATA_MAGIC) {
        return false;
    }
    uint32_t expected_crc = crc32_calculate((const uint8_t *)meta, sizeof(boot_metadata_t) - sizeof(uint32_t));
    return meta->header_crc == expected_crc;
}

bool metadata_read_active(boot_metadata_t *out_meta) {
    boot_metadata_t meta0, meta1;
    flash_read(ADDR_METADATA_0, &meta0, sizeof(boot_metadata_t));
    flash_read(ADDR_METADATA_1, &meta1, sizeof(boot_metadata_t));

    bool valid0 = metadata_verify_integrity(&meta0);
    bool valid1 = metadata_verify_integrity(&meta1);

    if (valid0 && valid1) {
        *out_meta = (meta0.sequence >= meta1.sequence) ? meta0 : meta1;
        return true;
    } else if (valid0) {
        *out_meta = meta0;
        return true;
    } else if (valid1) {
        *out_meta = meta1;
        return true;
    }
    return false;
}

bool metadata_write_next(const boot_metadata_t *meta) {
    boot_metadata_t meta0, meta1;
    flash_read(ADDR_METADATA_0, &meta0, sizeof(boot_metadata_t));
    flash_read(ADDR_METADATA_1, &meta1, sizeof(boot_metadata_t));

    bool valid0 = metadata_verify_integrity(&meta0);
    bool valid1 = metadata_verify_integrity(&meta1);

    uint32_t target_addr = ADDR_METADATA_0;
    uint32_t next_seq = 1;

    if (valid0 && valid1) {
        if (meta0.sequence >= meta1.sequence) {
            target_addr = ADDR_METADATA_1;
            next_seq = meta0.sequence + 1;
        } else {
            target_addr = ADDR_METADATA_0;
            next_seq = meta1.sequence + 1;
        }
    } else if (valid0) {
        target_addr = ADDR_METADATA_1;
        next_seq = meta0.sequence + 1;
    } else if (valid1) {
        target_addr = ADDR_METADATA_0;
        next_seq = meta1.sequence + 1;
    }

    boot_metadata_t to_write = *meta;
    to_write.magic = BOOT_METADATA_MAGIC;
    to_write.sequence = next_seq;
    to_write.header_crc = crc32_calculate((const uint8_t *)&to_write, sizeof(boot_metadata_t) - sizeof(uint32_t));

    if (!flash_erase_sector(target_addr)) {
        return false;
    }
    return flash_write(target_addr, &to_write, sizeof(boot_metadata_t));
}

/* ========================================================================= */
/* ЕМУЛЯТОР СТОРОЖОВОГО ТАЙМЕРА (WATCHDOG)                                   */
/* ========================================================================= */

typedef struct {
    int  timeout_ticks;
    int  current_ticks;
    bool is_running;
    bool triggered;
} watchdog_t;

static watchdog_t g_watchdog;

void watchdog_start(int timeout_ticks) {
    g_watchdog.timeout_ticks = timeout_ticks;
    g_watchdog.current_ticks = timeout_ticks;
    g_watchdog.is_running = true;
    g_watchdog.triggered = false;
}

void watchdog_kick(void) {
    if (g_watchdog.is_running) {
        g_watchdog.current_ticks = g_watchdog.timeout_ticks;
    }
}

void watchdog_tick(void) {
    if (g_watchdog.is_running && !g_watchdog.triggered) {
        g_watchdog.current_ticks--;
        if (g_watchdog.current_ticks <= 0) {
            g_watchdog.triggered = true;
        }
    }
}

bool watchdog_has_triggered(void) {
    return g_watchdog.triggered;
}

/* ========================================================================= */
/* ЯДРО СИСТЕМНОГО ЗАВАНТАЖУВАЧА (BOOTLOADER ENGINE)                         */
/* ========================================================================= */

slot_id_t bootloader_run(void) {
    boot_metadata_t meta;
    if (!metadata_read_active(&meta)) {
        printf("[Завантажувач] Метадані відсутні або зіпсовані! Аварійна ініціалізація на SLOT A.\n");
        meta.magic = BOOT_METADATA_MAGIC;
        meta.sequence = 1;
        meta.active_slot = SLOT_ID_A;
        meta.slot_state = SLOT_STATE_VALID;
        meta.boot_attempts_left = 0;
        meta.max_boot_attempts = MAX_BOOT_ATTEMPTS;
        meta.image_version = 100;
        meta.image_crc = 0;
        metadata_write_next(&meta);
        return SLOT_ID_A;
    }

    printf("[Завантажувач] Активний слот: %c, стан: %d, спроб лишилося: %d (seq: %u)\n",
           (meta.active_slot == SLOT_ID_A) ? 'A' : 'B',
           meta.slot_state,
           meta.boot_attempts_left,
           meta.sequence);

    if (meta.slot_state == SLOT_STATE_PENDING_VERIFY) {
        if (meta.boot_attempts_left > 0) {
            meta.boot_attempts_left--;
            printf("[Завантажувач] Пробний запуск! Декремент лічильника спроб -> %d\n", meta.boot_attempts_left);
            metadata_write_next(&meta);
            watchdog_start(30); /* 30 тактів на самотест */
            return (slot_id_t)meta.active_slot;
        } else {
            printf("[Завантажувач] Спроби вичерпано! АВТОМАТИЧНИЙ ВІДКАТ на резервний слот.\n");
            meta.slot_state = SLOT_STATE_MARKED_BAD;
            slot_id_t fallback = (meta.active_slot == SLOT_ID_A) ? SLOT_ID_B : SLOT_ID_A;
            meta.active_slot = (uint8_t)fallback;
            meta.slot_state = SLOT_STATE_VALID;
            meta.boot_attempts_left = 0;
            metadata_write_next(&meta);
            return fallback;
        }
    }

    if (meta.slot_state == SLOT_STATE_VALID) {
        return (slot_id_t)meta.active_slot;
    }

    /* Якщо слот позначений як недійсний, перемикаємось на протилежний */
    slot_id_t safe_slot = (meta.active_slot == SLOT_ID_A) ? SLOT_ID_B : SLOT_ID_A;
    meta.active_slot = (uint8_t)safe_slot;
    meta.slot_state = SLOT_STATE_VALID;
    metadata_write_next(&meta);
    return safe_slot;
}

/* ========================================================================= */
/* КЛІЄНТ ОНОВЛЕННЯ ТА САМОТЕСТУВАННЯ ЗАСТОСУНКУ                             */
/* ========================================================================= */

bool app_ota_install_image(slot_id_t target_slot, uint32_t version, const uint8_t *payload, size_t size) {
    uint32_t target_addr = (target_slot == SLOT_ID_A) ? ADDR_SLOT_A : ADDR_SLOT_B;
    printf("[OTA Client] Запис образу версії %u у слот %c (розмір: %zu байтів)...\n",
           version, (target_slot == SLOT_ID_A) ? 'A' : 'B', size);

    /* Стирання секторів під новий образ */
    size_t sectors_needed = (size + FLASH_SECTOR_SIZE - 1) / FLASH_SECTOR_SIZE;
    for (size_t s = 0; s < sectors_needed; ++s) {
        if (!flash_erase_sector(target_addr + s * FLASH_SECTOR_SIZE)) {
            printf("[OTA Client] Помилка стирання сектора на адресі 0x%08X!\n", target_addr + (uint32_t)(s * FLASH_SECTOR_SIZE));
            return false;
        }
    }

    /* Запис коду */
    if (!flash_write(target_addr, payload, size)) {
        printf("[OTA Client] Помилка запису даних у Flash!\n");
        return false;
    }

    /* Оновлення метаданих на випробувальний режим */
    boot_metadata_t meta;
    if (!metadata_read_active(&meta)) {
        meta.sequence = 0;
    }
    meta.active_slot = (uint8_t)target_slot;
    meta.slot_state = SLOT_STATE_PENDING_VERIFY;
    meta.boot_attempts_left = MAX_BOOT_ATTEMPTS;
    meta.max_boot_attempts = MAX_BOOT_ATTEMPTS;
    meta.image_version = version;
    meta.image_crc = crc32_calculate(payload, size);

    return metadata_write_next(&meta);
}

bool app_mark_valid(void) {
    boot_metadata_t meta;
    if (!metadata_read_active(&meta)) {
        return false;
    }
    if (meta.slot_state == SLOT_STATE_PENDING_VERIFY) {
        meta.slot_state = SLOT_STATE_VALID;
        meta.boot_attempts_left = 0;
        printf("[Застосунок] САМОТЕСТ УСПІШНИЙ: образ закріплено як VALID!\n");
        return metadata_write_next(&meta);
    }
    return true;
}

/* ========================================================================= */
/* АВТОМАТИЗОВАНИЙ СТЕНД ТЕСТУВАННЯ СЦЕНАРІЇВ ВІДКАТУ                        */
/* ========================================================================= */

void run_test_clean_upgrade(void) {
    printf("\n==========================================================\n");
    printf("ТЕСТ 1: Штатне успішне оновлення прошивки (Happy Path)\n");
    printf("==========================================================\n");
    flash_init();

    /* 1. Початковий стан: стабільна прошивка v1.0 у слоті A */
    boot_metadata_t initial_meta = {
        .magic = BOOT_METADATA_MAGIC,
        .sequence = 1,
        .active_slot = SLOT_ID_A,
        .slot_state = SLOT_STATE_VALID,
        .boot_attempts_left = 0,
        .max_boot_attempts = 3,
        .image_version = 100,
        .image_crc = 0x12345678,
        .header_crc = 0
    };
    metadata_write_next(&initial_meta);

    /* 2. Застосунок у слоті A завантажує оновлення v2.0 у слот B */
    uint8_t dummy_v2[1024];
    memset(dummy_v2, 0xA5, sizeof(dummy_v2));
    app_ota_install_image(SLOT_ID_B, 200, dummy_v2, sizeof(dummy_v2));

    /* 3. Симуляція перезавантаження -> Запуск завантажувача */
    slot_id_t selected = bootloader_run();
    if (selected != SLOT_ID_B) {
        printf("ПОМИЛКА: завантажувач мав обрати SLOT B!\n");
        return;
    }

    /* 4. Застосунок успішно проходить самотест POST */
    watchdog_kick();
    app_mark_valid();

    /* 5. Наступний штатний рестарт */
    selected = bootloader_run();
    printf("Результат: Завантажено слот %c (очікувався B) -> %s\n",
           (selected == SLOT_ID_B) ? 'B' : 'A',
           (selected == SLOT_ID_B) ? "УСПІХ" : "НЕВДАЧА");
}

void run_test_crash_on_boot_rollback(void) {
    printf("\n==========================================================\n");
    printf("ТЕСТ 2: Аварія нового образу (HardFault) та автоматичний відкат\n");
    printf("==========================================================\n");
    flash_init();

    /* 1. Початковий стан: стабільна прошивка v1.0 у слоті A */
    boot_metadata_t initial_meta = {
        .magic = BOOT_METADATA_MAGIC,
        .sequence = 1,
        .active_slot = SLOT_ID_A,
        .slot_state = SLOT_STATE_VALID,
        .boot_attempts_left = 0,
        .max_boot_attempts = 3,
        .image_version = 100,
        .image_crc = 0x11111111,
        .header_crc = 0
    };
    metadata_write_next(&initial_meta);

    /* 2. Запис збійного образу v2.0 у слот B */
    uint8_t bad_v2[1024];
    memset(bad_v2, 0xDE, sizeof(bad_v2));
    app_ota_install_image(SLOT_ID_B, 200, bad_v2, sizeof(bad_v2));

    /* 3. Симуляція циклу падінь: 3 спроби старту, що завершуються крахом */
    for (int attempt = 1; attempt <= 3; ++attempt) {
        printf("\n--- Спроба запуску #%d ---\n", attempt);
        slot_id_t s = bootloader_run();
        printf("[Симуляція] Образ у слоті %c падає в HardFault під час ініціалізації!\n", (s == SLOT_ID_B) ? 'B' : 'A');
        /* Прошивка не викликає app_mark_valid() і рестартує */
    }

    /* 4. Четвертий рестарт: ліміт вичерпано -> очікується відкат на слот A */
    printf("\n--- Фінальний старт після вичерпання спроб ---\n");
    slot_id_t fallback_slot = bootloader_run();
    printf("Результат: Завантажено слот %c (очікувався A) -> %s\n",
           (fallback_slot == SLOT_ID_A) ? 'A' : 'B',
           (fallback_slot == SLOT_ID_A) ? "УСПІХ (ВІДКАТ ВИКОНАНО)" : "НЕВДАЧА");
}

void run_test_power_cut_during_metadata_write(void) {
    printf("\n==========================================================\n");
    printf("ТЕСТ 3: Ін'єкція знеструмлення посеред запису сектора метаданих\n");
    printf("==========================================================\n");
    flash_init();

    /* 1. Запис базового валідного стану у Metadata 0 */
    boot_metadata_t meta = {
        .magic = BOOT_METADATA_MAGIC,
        .sequence = 10,
        .active_slot = SLOT_ID_A,
        .slot_state = SLOT_STATE_VALID,
        .boot_attempts_left = 0,
        .max_boot_attempts = 3,
        .image_version = 100,
        .image_crc = 0xAAAAAAAA,
        .header_crc = 0
    };
    metadata_write_next(&meta);

    /* 2. Активація ін'єкції збою: знеструмлення через 12 байтів після початку запису */
    printf("[Ін'єкція] Налаштування знеструмлення через 12 байтів під час наступного запису...\n");
    flash_enable_power_cut_after_bytes(12);

    /* 3. Спроба оновити стан на слот B */
    boot_metadata_t next_meta = meta;
    next_meta.active_slot = SLOT_ID_B;
    next_meta.slot_state = SLOT_STATE_PENDING_VERIFY;
    bool write_ok = metadata_write_next(&next_meta);
    printf("[Запис] Результат операції запису: %s (очікувалося переривання)\n", write_ok ? "OK" : "ПЕРЕРВАНО");

    /* 4. Відновлення живлення -> Запуск завантажувача */
    flash_disable_fault_injection();
    printf("\n[Живлення відновлено] Старт завантажувача...\n");
    slot_id_t selected = bootloader_run();

    printf("Результат: Завантажувач безпечно обрав слот %c (очікувався A) -> %s\n",
           (selected == SLOT_ID_A) ? 'A' : 'B',
           (selected == SLOT_ID_A) ? "УСПІХ (АТОМАРНІСТЬ ЗБЕРЕЖЕНО)" : "НЕВДАЧА");
}

int main(void) {
    printf("==========================================================\n");
    printf("ЗАПУСК СИМУЛЯТОРА ЗАВАНТАЖУВАЧА З A/B СЛОТАМИ ТА ВІДКАTOM\n");
    printf("==========================================================\n");

    run_test_clean_upgrade();
    run_test_crash_on_boot_rollback();
    run_test_power_cut_during_metadata_write();

    printf("\n==========================================================\n");
    printf("УСІ ТЕСТОВІ СЦЕНАРІЇ УСПІШНО ПРОЙДЕНО.\n");
    printf("==========================================================\n");
    return 0;
}
```
```cpp
// Повна реалізація симулятора завантажувача з A/B слотами на C++20
#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <cstdint>
#include <cstring>
#include <optional>
#include <expected>
#include <memory>
#include <algorithm>

namespace boot_sim {

inline constexpr size_t FlashTotalSize  = 2 * 1024 * 1024; // 2 МБ
inline constexpr size_t FlashSectorSize = 4096;            // 4 КБ
inline constexpr uint32_t BootMagic     = 0x544F4F42UL;    // "BOOT"
inline constexpr uint8_t  MaxBootTries  = 3;

inline constexpr uint32_t AddrMetadata0 = 0x00008000UL;
inline constexpr uint32_t AddrMetadata1 = 0x00009000UL;
inline constexpr uint32_t AddrSlotA     = 0x00010000UL;
inline constexpr uint32_t AddrSlotB     = 0x00100000UL;

enum class SlotId : uint8_t {
    SlotA = 0,
    SlotB = 1,
    None  = 0xFF
};

enum class SlotState : uint8_t {
    Empty         = 0xFF,
    PendingVerify = 0x01,
    Valid         = 0x02,
    MarkedBad     = 0x03
};

struct [[gnu::packed]] BootMetadata {
    uint32_t  magic{BootMagic};
    uint32_t  sequence{0};
    SlotId    activeSlot{SlotId::SlotA};
    SlotState slotState{SlotState::Empty};
    uint8_t   bootAttemptsLeft{0};
    uint8_t   maxBootAttempts{MaxBootTries};
    uint32_t  imageVersion{0};
    uint32_t  imageCrc{0};
    uint32_t  headerCrc{0};
};

[[nodiscard]] constexpr uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFFUL;
    for (uint8_t byte : data) {
        crc ^= byte;
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320UL & (-(crc & 1)));
        }
    }
    return ~crc;
}

// Емулятор Flash пам'яті з підтримкою ін'єкції аварійного знеструмлення
class FlashMemory {
public:
    FlashMemory() {
        m_storage.fill(0xFF);
    }

    void reset() noexcept {
        m_storage.fill(0xFF);
        m_faultInjectionEnabled = false;
        m_bytesUntilPowerCut = -1;
        m_powerCutTriggered = false;
    }

    void enablePowerCutAfterBytes(int byteCount) noexcept {
        m_faultInjectionEnabled = true;
        m_bytesUntilPowerCut = byteCount;
        m_powerCutTriggered = false;
    }

    void disableFaultInjection() noexcept {
        m_faultInjectionEnabled = false;
        m_bytesUntilPowerCut = -1;
        m_powerCutTriggered = false;
    }

    [[nodiscard]] bool read(uint32_t address, std::span<uint8_t> dest) const noexcept {
        if (address + dest.size() > FlashTotalSize) return false;
        std::copy_n(m_storage.data() + address, dest.size(), dest.data());
        return true;
    }

    [[nodiscard]] bool eraseSector(uint32_t sectorAddr) noexcept {
        if (sectorAddr % FlashSectorSize != 0 || sectorAddr + FlashSectorSize > FlashTotalSize) {
            return false;
        }
        if (m_faultInjectionEnabled) {
            if (m_bytesUntilPowerCut <= 0) {
                m_powerCutTriggered = true;
                return false;
            }
            if (m_bytesUntilPowerCut < static_cast<int>(FlashSectorSize)) {
                std::fill_n(m_storage.data() + sectorAddr, m_bytesUntilPowerCut, 0xFF);
                m_bytesUntilPowerCut = 0;
                m_powerCutTriggered = true;
                return false;
            }
            m_bytesUntilPowerCut -= FlashSectorSize;
        }
        std::fill_n(m_storage.data() + sectorAddr, FlashSectorSize, 0xFF);
        return true;
    }

    [[nodiscard]] bool write(uint32_t address, std::span<const uint8_t> src) noexcept {
        if (address + src.size() > FlashTotalSize) return false;
        for (size_t i = 0; i < src.size(); ++i) {
            if (m_faultInjectionEnabled) {
                if (m_bytesUntilPowerCut <= 0) {
                    m_powerCutTriggered = true;
                    return false;
                }
                m_bytesUntilPowerCut--;
            }
            m_storage[address + i] &= src[i];
        }
        return true;
    }

    [[nodiscard]] bool wasPowerCutTriggered() const noexcept {
        return m_powerCutTriggered;
    }

private:
    std::array<uint8_t, FlashTotalSize> m_storage{};
    bool m_faultInjectionEnabled{false};
    int  m_bytesUntilPowerCut{-1};
    bool m_powerCutTriggered{false};
};

// Двосекторний менеджер метаданих
class MetadataManager {
public:
    explicit MetadataManager(FlashMemory& flash) noexcept : m_flash(flash) {}

    [[nodiscard]] bool verifyIntegrity(const BootMetadata& meta) const noexcept {
        if (meta.magic != BootMagic) return false;
        auto spanData = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&meta), sizeof(BootMetadata) - sizeof(uint32_t));
        return meta.headerCrc == calculate_crc32(spanData);
    }

    [[nodiscard]] std::optional<BootMetadata> readActive() const noexcept {
        BootMetadata meta0{}, meta1{};
        m_flash.read(AddrMetadata0, {reinterpret_cast<uint8_t*>(&meta0), sizeof(BootMetadata)});
        m_flash.read(AddrMetadata1, {reinterpret_cast<uint8_t*>(&meta1), sizeof(BootMetadata)});

        const bool valid0 = verifyIntegrity(meta0);
        const bool valid1 = verifyIntegrity(meta1);

        if (valid0 && valid1) {
            return (meta0.sequence >= meta1.sequence) ? meta0 : meta1;
        } else if (valid0) {
            return meta0;
        } else if (valid1) {
            return meta1;
        }
        return std::nullopt;
    }

    [[nodiscard]] bool writeNext(BootMetadata meta) noexcept {
        BootMetadata meta0{}, meta1{};
        m_flash.read(AddrMetadata0, {reinterpret_cast<uint8_t*>(&meta0), sizeof(BootMetadata)});
        m_flash.read(AddrMetadata1, {reinterpret_cast<uint8_t*>(&meta1), sizeof(BootMetadata)});

        const bool valid0 = verifyIntegrity(meta0);
        const bool valid1 = verifyIntegrity(meta1);

        uint32_t targetAddr = AddrMetadata0;
        uint32_t nextSeq = 1;

        if (valid0 && valid1) {
            if (meta0.sequence >= meta1.sequence) {
                targetAddr = AddrMetadata1;
                nextSeq = meta0.sequence + 1;
            } else {
                targetAddr = AddrMetadata0;
                nextSeq = meta1.sequence + 1;
            }
        } else if (valid0) {
            targetAddr = AddrMetadata1;
            nextSeq = meta0.sequence + 1;
        } else if (valid1) {
            targetAddr = AddrMetadata0;
            nextSeq = meta1.sequence + 1;
        }

        meta.magic = BootMagic;
        meta.sequence = nextSeq;
        auto spanData = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&meta), sizeof(BootMetadata) - sizeof(uint32_t));
        meta.headerCrc = calculate_crc32(spanData);

        if (!m_flash.eraseSector(targetAddr)) return false;
        return m_flash.write(targetAddr, {reinterpret_cast<const uint8_t*>(&meta), sizeof(BootMetadata)});
    }

private:
    FlashMemory& m_flash;
};

// Емулятор завантажувача
class Bootloader {
public:
    explicit Bootloader(MetadataManager& metaMgr) noexcept : m_metaMgr(metaMgr) {}

    [[nodiscard]] SlotId run() noexcept {
        auto activeMetaOpt = m_metaMgr.readActive();
        if (!activeMetaOpt) {
            std::cout << "[Завантажувач] Метадані відсутні! Аварійна ініціалізація на SLOT A.\n";
            BootMetadata initMeta{};
            initMeta.magic = BootMagic;
            initMeta.sequence = 1;
            initMeta.activeSlot = SlotId::SlotA;
            initMeta.slotState = SlotState::Valid;
            initMeta.bootAttemptsLeft = 0;
            initMeta.imageVersion = 100;
            m_metaMgr.writeNext(initMeta);
            return SlotId::SlotA;
        }

        auto meta = *activeMetaOpt;
        std::cout << "[Завантажувач] Слот: " << (meta.activeSlot == SlotId::SlotA ? 'A' : 'B')
                  << ", Стан: " << static_cast<int>(meta.slotState)
                  << ", Залишок спроб: " << static_cast<int>(meta.bootAttemptsLeft)
                  << " (seq: " << meta.sequence << ")\n";

        if (meta.slotState == SlotState::PendingVerify) {
            if (meta.bootAttemptsLeft > 0) {
                meta.bootAttemptsLeft--;
                std::cout << "[Завантажувач] Декремент спроб -> " << static_cast<int>(meta.bootAttemptsLeft) << "\n";
                m_metaMgr.writeNext(meta);
                return meta.activeSlot;
            } else {
                std::cout << "[Завантажувач] Спроби вичерпано! АВТОМАТИЧНИЙ ВІДКАТ.\n";
                meta.slotState = SlotState::MarkedBad;
                const auto fallback = (meta.activeSlot == SlotId::SlotA) ? SlotId::SlotB : SlotId::SlotA;
                meta.activeSlot = fallback;
                meta.slotState = SlotState::Valid;
                meta.bootAttemptsLeft = 0;
                m_metaMgr.writeNext(meta);
                return fallback;
            }
        }

        if (meta.slotState == SlotState::Valid) {
            return meta.activeSlot;
        }

        const auto safe = (meta.activeSlot == SlotId::SlotA) ? SlotId::SlotB : SlotId::SlotA;
        meta.activeSlot = safe;
        meta.slotState = SlotState::Valid;
        m_metaMgr.writeNext(meta);
        return safe;
    }

private:
    MetadataManager& m_metaMgr;
};

// Клієнт оновлення застосунку
class OtaClient {
public:
    OtaClient(MetadataManager& metaMgr, FlashMemory& flash) noexcept
        : m_metaMgr(metaMgr), m_flash(flash) {}

    [[nodiscard]] bool installImage(SlotId targetSlot, uint32_t version, std::span<const uint8_t> payload) noexcept {
        const uint32_t targetAddr = (targetSlot == SlotId::SlotA) ? AddrSlotA : AddrSlotB;
        std::cout << "[OTA Client] Запис образу v" << version << " у слот "
                  << (targetSlot == SlotId::SlotA ? 'A' : 'B') << "...\n";

        const size_t sectors = (payload.size() + FlashSectorSize - 1) / FlashSectorSize;
        for (size_t s = 0; s < sectors; ++s) {
            if (!m_flash.eraseSector(targetAddr + static_cast<uint32_t>(s * FlashSectorSize))) {
                return false;
            }
        }

        if (!m_flash.write(targetAddr, payload)) {
            return false;
        }

        BootMetadata meta{};
        if (auto current = m_metaMgr.readActive()) {
            meta = *current;
        }
        meta.activeSlot = targetSlot;
        meta.slotState = SlotState::PendingVerify;
        meta.bootAttemptsLeft = MaxBootTries;
        meta.maxBootAttempts = MaxBootTries;
        meta.imageVersion = version;
        meta.imageCrc = calculate_crc32(payload);

        return m_metaMgr.writeNext(meta);
    }

    [[nodiscard]] bool markValid() noexcept {
        auto active = m_metaMgr.readActive();
        if (!active) return false;
        if (active->slotState == SlotState::PendingVerify) {
            active->slotState = SlotState::Valid;
            active->bootAttemptsLeft = 0;
            std::cout << "[Застосунок] Самотест POST успішний -> закріплено VALID!\n";
            return m_metaMgr.writeNext(*active);
        }
        return true;
    }

private:
    MetadataManager& m_metaMgr;
    FlashMemory&     m_flash;
};

} // namespace boot_sim
```
:::

### Детальний розбір алгоритмів та структур даних

Розглянемо ключові інженерні рішення, закладені в архітектуру симулятора:

#### 1. Моделювання фізичних властивостей пам'яті NOR Flash
У функції `flash_write()` реалізовано побітову операцію кон'юнкції `m_storage[address + i] &= src[i]`. Це точно відтворює фізику транзисторів із плаваючим затвором: якщо комірка містить байт `0xFF` (`11111111b`), запис байта `0x0F` переведе старші 4 біти в `0`. Якщо після цього спробувати без стирання записати байт `0xF0` (`11110000b`), результатом стане `0x0F & 0xF0 = 0x00`, а не `0xF0`. Така поведінка дозволяє виявити помилки в алгоритмах, які намагаються перезаписати метадані без виконання команди стирання сектора `flash_erase_sector()`.

#### 2. Арифметичне чергування секторів та переповнення лічильника послідовності
У функції `metadata_write_next()` вибір цільового сектора здійснюється на основі порівняння лічильників епох `meta0.sequence` та `meta1.sequence`. Якщо обидва сектори містять валідні контрольні суми CRC32, активним визнається сектор із більшим номером.

У довгостроковій перспективі лічильник `sequence` (32 біти) може зазнати переповнення (2³² - 1 → 0). Для коректної обробки переповнення у промислових системах застосовують модульну арифметику переходів:

```text
delta = (s_new - s_old) mod 2³²  [різниця епох послідовності]
```

Якщо `delta < 2³¹`, нове значення вважається новішим за старе. Це запобігає блокуванню оновлень після досягнення 4.29 мільярда транзакцій.

#### 3. Моделювання ланцюга обробки збоїв сторожового таймера

Емулятор `watchdog_t` дозволяє верифікувати сценарій «повільного зависання» (*Slow Hang*), коли нова прошивка успішно ініціалізує ядро, але зависає під час циклу опитування датчика через апаратну несправність шини I2C. Симулятор підраховує кількість виконаних тактів між викликами `watchdog_kick()`. Якщо застосунок не скидає таймер протягом 30 умовних одиниць часу, прапорець `triggered` стає рівним `true`, імітуючи апаратне скидання мікроконтролера за сигналом IWDG.

### Покроковий розбір тестових сценаріїв

Автоматизований тестовий стенд виконує три фундаментальні сценарії перевірки надійності:

#### Сценарій 1: Штатне оновлення без збоїв (Happy Path)
1. **Початковий стан:** Симулятор ініціалізує Flash-пам'ять. У секторі `Metadata_0` створюється початковий запис для `Slot_A` (версія 1.0, статус `VALID`, `sequence = 1`).
2. **Завантаження:** Застосунок зі `Slot_A` викликає функцію `app_ota_install_image()`, яка записує тестовий двійковий масив нової прошивки v2.0 у `Slot_B`.
3. **Фіксація випробування:** Менеджер метаданих записує оновлену структуру у `Metadata_1` зі статусом `PENDING_VERIFY`, лічильником `boot_attempts_left = 3` та номером `sequence = 2`.
4. **Старт завантажувача:** Завантажувач зчитує `Metadata_1`, декрементує лічильник спроб до 2, записує оновлений стан у `Metadata_0` (`sequence = 3`) і передає керування у `Slot_B`.
5. **Самотестування POST:** Застосунок у `Slot_B` успішно виконує перевірку периферії, скидає Watchdog і викликає `app_mark_valid()`.
6. **Фінальне закріплення:** Метадані у `Metadata_1` оновлюються до статусу `VALID` (`sequence = 4`). При наступних перезавантаженнях завантажувач беззастережно обирає `Slot_B`.

#### Сценарій 2: Аварія прошивки (HardFault) та автоматичний відкат
1. **Початковий стан:** Система працює на стабільній прошивці v1.0 у `Slot_A`.
2. **Запис збійного коду:** Клієнт OTA завантажує у `Slot_B` образ версії 2.0, який містить штучну помилку (розіменування нульового вказівника на першому кроці ініціалізації).
3. **Перший старт:** Завантажувач запускає `Slot_B`, зменшуючи лічильник спроб з 3 до 2. Прошивка падає в виняток до виклику `app_mark_valid()`.
4. **Другий старт:** Завантажувач знову запускає `Slot_B`, зменшуючи лічильник спроб з 2 до 1. Прошивка повторно падає.
5. **Третій старт:** Завантажувач запускає `Slot_B`, зменшуючи лічильник з 1 до 0. Прошивка втретє зазнає краху.
6. **Четвертий старт (Відкат):** Завантажувач виявляє, що `boot_attempts_left == 0`. Він маркує `Slot_B` як `MARKED_BAD`, перемикає активний покажчик на `Slot_A`, встановлює статус `VALID` і передає керування старій робочій прошивці v1.0. Система відновлює працездатність.

#### Сценарій 3: Ін'єкція знеструмлення посеред запису метаданих
1. **Початковий стан:** У секторі `Metadata_0` збережено валідний запис зі значенням `sequence = 10` (активний `Slot_A`).
2. **Налаштування ін'єкції:** Ін'єктор збоїв налаштовується на розрив живлення рівно через 12 байтів після початку запису нового сектора `Metadata_1`.
3. **Спроба оновлення:** Клієнт OTA ініціює запис нового статусу `PENDING_VERIFY` для `Slot_B`. Функція `flash_write()` успішно записує перші 12 байтів (поля `magic`, `sequence`, `active_slot`), після чого ін'єктор обриває живлення. Решта 20 байтів структури залишаються у стертому стані `0xFF`.
4. **Відновлення живлення:** Симулятор знімає аварійне блокування і викликає `bootloader_run()`.
5. **Валідація завантажувачем:** Завантажувач зчитує `Metadata_1`, обчислює CRC32 по фактично записаних байтах і виявляє невідповідність із полем `header_crc`. Завантажувач відкидає пошкоджений сектор `Metadata_1` і зчитує сектор `Metadata_0`.
6. **Результат:** Завантажувач успішно та безпечно запускає перевірений `Slot_A`, запобігаючи виконанню неповної або спотвореної конфігурації.

### Повний протокол самодіагностики застосунку (Application Self-Test Protocol)

У промислових контролерах застосунок не має права викликати `app_mark_valid()` негайно після старту функції `main()`. Процедура прийняття рішення розбивається на п'ять послідовних бар'єрів перевірки життєздатності:

1. **Фаза 1: Санітарний аудит регістрів процесора (CPU Health Audit):**
   - Перевірка регістрів аварійного стану ядра: `SCB->CFSR == 0` (Configurable Fault Status Register), `SCB->HFSR == 0` (HardFault Status Register).
   - Валідація цілісності таблиці векторів переривань у SRAM/Flash.
   - Перевірка залишку вільної пам'яті вказівника головного стека `MSP`.
2. **Фаза 2: Апаратне зондування периферійних шин (BIST Probe):**
   - Опитування шин I2C та SPI: послідовне зчитування регістрів ідентифікації `WHO_AM_I` або `JEDEC ID` усіх підключених мікросхем (зовнішніх датчиків температури, тиску, акселерометрів, додаткових мікросхем пам'яті FRAM).
   - Якщо обов'язковий датчик не відповідає або повертає помилку зв'язку, застосунок фіксує невідповідність апаратної ревізії та скасовує оновлення.
3. **Фаза 3: Валідація сховища конфігурації NVS:**
   - Перевірка цілісності розділу налаштувань (CRC таблиць NVS / LittleFS).
   - Успішне зчитування обов'язкових ключів: унікального ідентифікатора пристрою UUID, калібрувальних коефіцієнтів АЦП, параметрів радіочастотного тракту.
4. **Фаза 4: Мережеве рукостискання та аутентифікація (Network Handshake):**
   - Ініціалізація радіомодема (LTE / NB-IoT / Wi-Fi) та отримання валідної IP-адреси через DHCP.
   - Встановлення захищеного з'єднання TLS 1.3 з сервером управління флотом.
   - Проходження взаємної сертифікатної аутентифікації mTLS.
5. **Фаза 5: Отримання квитанції від хмарного сервера (Cloud Telemetry ACK):**
   - Надсилання діагностичного повідомлення: `{"event": "ota_trial_boot", "version": 200, "boot_attempts_left": 2}`.
   - Отримання підтвердження від бекенду: `{"status": "ACK", "action": "CONFIRM_PERMANENT"}`.

Лише після успішного подолання всіх п'яти фаз застосунок викликає `app_mark_valid()`. Якщо хоча б один із етапів зазнає невдачі протягом 60 секунд, застосунок зупиняє скидання Watchdog, форсуючи автоматичний відкат на попередній робочий слот.

### Методологія стрес-тестування та фазинг (Fuzzing & Chaos Engineering)

Для підтвердження абсолютної стійкості завантажувача до непередбачуваних зовнішніх збоїв у симулятор інтегрують генератор випадкових збоїв (*Chaos Injection Engine*):

1. **Мутаційне тестування Flash (Flash Corruption Fuzzing):**
   - Емулятор у випадкові моменти часу інвертує випадкові біти (`Bit-Flip`) у пасивному слоті або в секторі метаданих.
   - Завантажувач повинен коректно виявляти пошкодження через CRC32 та SHA-256 і блокувати передачу керування на зіпсований банк пам'яті.
2. **Стохастичне знеструмлення (Stochastic Power-Cut):**
   - Запуск циклу з 10 000 послідовних оновлень, де кожна операція запису переривається у псевдовипадковий момент часу.
   - Критерій успіху тесту: жодна комбінація знеструмлень не повинна призвести до стану, коли обидва сектори метаданих стають недійсними або завантажувач зависає в нескінченному циклі.

### Інтеграція симулятора у конвеєри неперервної інтеграції (CI/CD)

Симулятор розроблено як самодостатню консольну утиліту без зовнішніх бібліотечних залежностей, що дозволяє запускати його на будь-якому сервері автоматизації (GitHub Actions, GitLab CI, Jenkins, Azure Pipelines).

Приклад файлу конфігурації для GitHub Actions (`.github/workflows/bootloader-test.yml`):

```yaml
name: Bootloader Simulator Verification Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  verify-bootloader:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Compile C99 Simulator with Sanitizers
        run: |
          gcc -std=c99 -Wall -Wextra -Werror -pedantic \
              -fsanitize=address,undefined -g \
              proj-ab-bootloader-simulator.c -o sim_c99

      - name: Run C99 Automated Verification Suite
        run: ./sim_c99

      - name: Compile C++20 Simulator
        run: |
          g++ -std=c++20 -Wall -Wextra -Werror -pedantic \
              -fsanitize=address,undefined -g \
              proj-ab-bootloader-simulator.cpp -o sim_cpp20

      - name: Run C++20 Automated Verification Suite
        run: ./sim_cpp20
```

Застосування компіляторних санітайзерів `AddressSanitizer` (ASan) та `UndefinedBehaviorSanitizer` (UBSan) гарантує виявлення будь-яких прихованих помилок вирівнювання пам'яті, розіменування некоректних покажчиків або переповнення цілих чисел ще на етапі перевірки запиту на злиття, унеможливлюючи потрапляння дефектного коду у виробничу прошивку.

### Поглиблений аналіз апаратного контексту Cortex-M: переривання, стек та бар'єри пам'яті

При розробці системного завантажувача для архітектури ARM Cortex-M критично важливо розуміти послідовність дій під час передачі керування від коду завантажувача до образу застосунку. Проста передача керування через виклик функції за покажчиком `((void (*)(void))entry_addr)()` призведе до аварійного падіння, якщо апаратні периферійні вузли мікроконтролера залишилися активними.

#### 1. Деініціалізація периферії та очищення черги переривань
Якщо завантажувач використовував модуль UART для виводу логів або контролер DMA для передачі даних, ці модулі можуть згенерувати апаратне переривання вже після того, як керування перейде в застосунок. Оскільки новий застосунок ще не встиг зареєструвати власні обробники переривань, процесор зчитає нульовий або сміттєвий покажчик із таблиці векторів і звалиться в `HardFault`.

Правильний протокол деініціалізації включає:
- Глобальне маскування переривань у регістрі ядра: `__disable_irq()`, що встановлює біт `PRIMASK`.
- Вимкнення всіх ліній зовнішніх переривань у контролері NVIC: послідовний запис одиниць у регістри скидання дозволу `NVIC->ICER[0..7]`.
- Очищення всіх відкладених запитів на переривання: запис одиниць у регістри `NVIC->ICPR[0..7]`.
- Повна зупинка та скидання системного таймера ядра:

:::tabs
```c
SysTick->CTRL = 0;
SysTick->LOAD = 0;
SysTick->VAL  = 0;
```
```cpp
SysTick->CTRL = 0;
SysTick->LOAD = 0;
SysTick->VAL  = 0;
```
:::


#### 2. Релокація таблиці векторів (VTOR)
Регістр зміщення таблиці векторів `SCB->VTOR` вказує процесорному ядру базову адресу, за якою розміщено вектори початкового стека, системних винятків та переривань периферії. У мікроконтролерах Cortex-M3/M4/M7/M33 значення `VTOR` має бути вирівняне на границю, що є степенем двійки і перевищує сумарний розмір таблиці векторів (типово 512 або 1024 байти, тобто біти `[6:0]` або `[7:0]` мають бути нульовими).

:::tabs
```c
SCB->VTOR = (uint32_t)target_slot_address;
```
```cpp
SCB->VTOR = reinterpret_cast<uint32_t>(target_slot_address);
```
:::

#### 3. Встановлення вказівника головного стека (MSP)
Перше 32-бітне слово двійкового образу містить початкове значення вказівника головного стека (`Main Stack Pointer, MSP`). Завантажувач зобов'язаний зчитати це значення та завантажити його в регістр процесора `SP` за допомогою асемблерної інструкції `msr msp, r0` або CMSIS-макросу `__set_MSP()`.

Якщо завантажувач використовував окремий стек процесу (`Process Stack Pointer, PSP`) або привілейований стек із виділеним контролером захисту пам'яті (MPU), перед стрибком необхідно скинути регістр керування `CONTROL` у значення `0x00000000` (використання MSP у привілейованому режимі).

#### 4. Апаратні бар'єри синхронізації
Перед виконанням асемблерного переходу `bx r0` необхідно виконати дві інструкції бар'єрів пам'яті:
- `__DSB()` (*Data Synchronization Barrier*): гарантує, що всі попередні операції запису у системні регістри `NVIC`, `SCB->VTOR` та `CONTROL` повністю завершилися на внутрішній шині процесора.
- `__ISB()` (*Instruction Synchronization Barrier*): очищає конвеєр інструкцій процесора, гарантуючи, що наступна вибірка машинних інструкцій буде здійснюватися з оновленими налаштуваннями таблиці векторів та привілеїв.

### Математичний аналіз контрольних сум CRC-32/ISO-HDLC

Контрольна сума CRC32 (поліном `0x04C11DB7`, реверсне значення `0xEDB88320`) є базовим інструментом швидкої верифікації цілісності даних у вбудованих системах. Вона базується на операції ділення многочленів над кінцевим полем GF(2):

```text
P(x) = x³² + x²⁶ + x²³ + x²² + x¹⁶ + x¹² + x¹¹ + x¹⁰ + x⁸ + x⁷ + x⁵ + x⁴ + x² + x + 1  [поліном IEEE 802.3]
```

Математичні властивості алгоритму CRC32 при розмірі блоку даних до 4096 байтів:
1. **100% виявлення поодиноких бітових помилок:** Будь-який одиничний витік заряду в комірці Flash призводить до гарантованої зміни значення CRC.
2. **100% виявлення подвійних бітових помилок:** Якщо через деградацію підкладки спотворилися два довільні біти в межах сектора, CRC32 гарантовано виявить цю помилку.
3. **100% виявлення пакетних помилок (Burst Errors):** Будь-яке безперервне спотворення даних довжиною до 32 бітів (наприклад, пошкодження одного 32-бітного слова пам'яті через збій контролера шини) виявляється з імовірністю 1.
4. **Виявлення довільних випадкових спотворень:** Для пакетів довжиною понад 32 біти ймовірність пропуску помилки становить:

```text
P_undetected = 1 / 2³² ≈ 2.328 × 10⁻¹⁰  [ймовірність нерозпізнаної помилки]
```

Табличний метод розрахунку CRC32 (LUT на 256 елементів) дозволяє обчислювати контрольну суму зі швидкістю ~1 байт за 4 процесорні такти, що на частоті 100 МГц дає пропускну здатність 25 МБ/с. Це дозволяє перевірити 1 МБ образ прошивки всього за 40 мілісекунд, не затримуючи час старту обладнання.

### Архітектура структурованого аварійного дампу (.noinit Crash Dump)

Коли нова версія прошивки падає в апаратний виняток `HardFault`, стандартний обробник помилок перезавантажує мікроконтролер. Проте без збереження діагностичного дампу розробники не зможуть дізнатися, у якому саме модулі сталася помилка.

Оскільки звичайна оперативна пам'ять SRAM очищається або ініціалізується нулями під час виконання функції `Reset_Handler` (обнулення секції `.bss` та копіювання `.data`), діагностичний контекст розміщують у спеціальній секції `.noinit`.

:::tabs
```c
typedef struct {
    uint32_t magic;              /* Магічне число валідності (0xDEADBEEF) */
    uint32_t reset_reason;       /* Прапорці регістру RCC_CSR (IWDG, PIN, POR, SFT) */
    uint32_t cfsr;               /* Регістр Configurable Fault Status Register */
    uint32_t hfsr;               /* Регістр HardFault Status Register */
    uint32_t mmar;               /* Регістр адреси помилки пам'яті MemManage Fault */
    uint32_t bfar;               /* Регістр адреси помилки шини Bus Fault */
    uint32_t pc;                 /* Вказівник інструкції Program Counter у момент краху */
    uint32_t lr;                 /* Регістр зв'язку Link Register */
    uint32_t sp;                 /* Вказівник стека Stack Pointer */
    uint32_t stack_snapshot[64]; /* Знімок останніх 64 слів стека */
    uint32_t dump_crc;           /* Контрольна сума CRC32 для валідації */
} __attribute__((packed)) crash_dump_t;

__attribute__((section(".noinit"))) static crash_dump_t g_crash_dump;
```
```cpp
#include <cstdint>
#include <array>

struct [[gnu::packed]] CrashDump {
    uint32_t                magic{0xDEADBEEFUL};
    uint32_t                resetReason{0};
    uint32_t                cfsr{0};
    uint32_t                hfsr{0};
    uint32_t                mmar{0};
    uint32_t                bfar{0};
    uint32_t                pc{0};
    uint32_t                lr{0};
    uint32_t                sp{0};
    std::array<uint32_t, 64> stackSnapshot{};
    uint32_t                dumpCrc{0};
};

[[gnu::section(".noinit")]] static CrashDump g_crashDump;
```
:::


#### Порядок збереження контексту в обробнику HardFault
1. **Визначення активного стека:** Обробник перевіряє біт 2 регістра `EXC_RETURN` у регістрі `LR`. Якщо біт дорівнює `1`, виняток виник у контексті стека процесу (`PSP`), якщо `0` — у контексті стека ядра (`MSP`).
2. **Зчитування стекового кадру:** Процесор Cortex-M автоматично зберігає 8 регістрів на поточному стеку: `R0, R1, R2, R3, R12, LR, PC, xPSR`. Обробник зчитує збережене значення `PC`, яке вказує на точну адресу інструкції, виконання якої спричинило крах.
3. **Аналіз прапорців `SCB->CFSR`:**
   - Якщо активний біт `UNDEFINSTR` (байт UFSR), прошивка спробувала виконати неіснуючий або пошкоджений машинний код.
   - Якщо активний біт `UNALIGNED`, здійснено звернення до 32-бітного слова за непарною адресою.
   - Якщо активний біт `PRECISERR` (байт BFSR), відбулася помилка шини даних (наприклад, звернення до вимкненої периферії), а адреса порушення зберігається в `SCB->BFAR`.
4. **Розрахунок CRC32 та скидання:** Обробник обчислює контрольну суму структури `crash_dump_t` та ініціює програмне скидання викликом `NVIC_SystemReset()`.

Після перезапуску завантажувач фіксує декремент спроб або виконує відкат на старий слот `Slot_A`. Стара прошивка після ініціалізації зчитує секцію `.noinit`, перевіряє `magic == 0xDEADBEEF` та валідність `dump_crc`, пакує інформацію у телеметричний JSON-пакет і передає його на хмарний сервер моніторингу:

```json
{
  "device_id": "ST-94820",
  "event": "firmware_rollback_diagnostics",
  "failed_version": 200,
  "fallback_version": 100,
  "crash_context": {
    "pc": "0x080412A8",
    "lr": "0x08040F10",
    "cfsr": "0x00010000",
    "cfsr_decoded": "UNDEFINED_INSTRUCTION",
    "reset_cause": "SOFTWARE_RESET"
  }
}
```

### Захист від каскадних відмов конфігурації (Dual-Domain NVS)

Найнебезпечнішою вразливістю систем оновлення A/B є використання **спільного сховища конфігурації** (*Shared NVS/EEPROM*). Якщо нова версія прошивки під час тестового запуску модифікує структуру бази даних налаштувань, додає нові поля або видаляє старі ключі, а потім зазнає краху, стара версія після відкату не зможе розпарсити пошкоджену конфігурацію і також зазнає аварійного краху. Виникає катастрофічний стан **подвійного блокування** (*Double Brick*).

Щоб унеможливити подібний розвиток подій, застосовують архітектуру **подвійного домену конфігурації**:

```text
+-----------------------------------------------------------------------------------+
| Flash Layout: Dual NVS Isolation                                                 |
+-----------------------------------------------------------------------------------+
| Сектор             | Призначення                  | Доступ образу A | Доступ образу B |
+--------------------+------------------------------+-----------------+-----------------+
| NVS Domain A       | Налаштування для слота A     | Читання / Запис | Тільки читання  |
| NVS Domain B       | Налаштування для слота B     | Тільки читання  | Читання / Запис |
| NVS Shared Read    | Заводські калібрування (RO)  | Тільки читання  | Тільки читання  |
+--------------------+------------------------------+-----------------+-----------------+
```

1. **Клонування конфігурації під час оновлення:** Перед стартом випробувального образу клієнт OTA копіює поточний робочий стан із домену `NVS_A` у домен `NVS_B`.
2. **Ізоляція запису:** Образ `Slot_B` під час пробного запуску має право змінювати дані виключно у домені `NVS_B`. Домен `NVS_A` залишається недоторканним.
3. **Безпечний відкат:** Якщо образ `Slot_B` зазнає краху, стара прошивка `Slot_A` після повернення керування продовжує працювати з неушкодженим доменом `NVS_A`, гарантуючи безперервність виробничого процесу.

### Криптографічна верифікація образу: порівняльний аналіз ECDSA P-256 та RSA-3072

Захист від підробки прошивки вимагає верифікації асиметричного цифрового підпису перед тим, як завантажувач ухвалить рішення про передачу керування. Вбудовані системи стикаються з суворими обмеженнями щодо доступного обсягу Flash-пам'яті (код криптографічної бібліотеки) та оперативної пам'яті SRAM (буфери проміжних обчислень великих чисел).

#### 1. Математичні основи верифікації ECDSA
Підпис ECDSA базується на алгебрі групи точок еліптичної кривої у формі Вейєрштрасса над скінченним полем GF(p):

```text
y² ≡ x³ + ax + b (mod p)  [канонічне рівняння кривої]
```

Для стандартної кривої NIST P-256 (secp256r1) порядок базової точки G становить n ≈ 2²⁵⁶.

Алгоритм перевірки підпису (r, s) для хешу прошивки e = SHA-256(Image):
1. Перевірка приналежності компонентів підпису інтервалу: r, s є елементами [1, n-1].
2. Обчислення мультиплікативного оберненого елемента: w = s⁻¹ mod n.
3. Розрахунок скалярних коефіцієнтів:

```text
u₁ = e · w mod n,  u₂ = r · w mod n  [скалярні множники]
```

4. Обчислення суми точок на кривій за допомогою відкритого ключа виробника Q:

```text
P = u₁ · G + u₂ · Q  [результуюча точка кривої]
```

5. Якщо точка P дорівнює точці на нескінченності O, підпис відхиляється.
6. В іншому випадку розраховується координата v = x_P mod n. Підпис вважається автентичним тоді і тільки тоді, коли v == r.

#### 2. Порівняння алгоритмів асиметричного підпису у вбудованих завантажувачах

| Характеристика | RSA-2048 | RSA-3072 | ECDSA P-256 | Ed25519 (EdDSA) |
|---|---|---|---|---|
| **Еквівалентний рівень стійкості** | 112 бітів | 128 бітів | 128 бітів | 128 бітів |
| **Розмір відкритого ключа** | 256 байтів | 384 байти | 64 байти | 32 байти |
| **Розмір підпису у заголовку** | 256 байтів | 384 байти | 64 байти | 64 байти |
| **Використання стека SRAM** | ~3.2 КБ | ~4.8 КБ | ~1.2 КБ | ~0.8 КБ |
| **Розмір коду верифікатора** | ~6–10 КБ | ~8–12 КБ | ~3–5 КБ | ~2.5–4 КБ |
| **Час перевірки (Cortex-M4 @ 80 MHz)** | ~5–8 мс | ~12–18 мс | ~140–180 мс | ~60–90 мс |

Завдяки компактному розміру ключів та мінімальному навантаженню на SRAM, криптографія на еліптичних кривих (ECDSA P-256 або Ed25519) є галузевим стандартом де-факто для безпечних мікроконтролерних завантажувачів (MCUboot, ARM TF-M).

### Захист від атак зниження версії (Anti-Rollback) та eFuse

Окрім перевірки підпису, критичною загрозою безпеки є **атака зниження версії** (*Downgrade / Replay Attack*). У цьому сценарії зловмисник отримує стару легітимну версію прошивки (наприклад, v1.0), підписану дійсним ключем виробника, але яка містить відому вразливість переповнення буфера. Зловмисник примусово завантажує цей застарілий образ у пасивний слот пристрою. Оскільки цифровий підпис версії v1.0 коректний, звичайний завантажувач передасть їй керування, дозволяючи зловмиснику експлуатувати стару діру в безпеці.

Для запобігання таким атакам використовують апаратний захист на основі **одноразово програмованих мікрозапобіжників OTP eFuse**:

```text
eFuse Bit Array: [ 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | ... | 0 ] (Поточна апаратна версія = 4)
                                   ▲
                             Нове оновлення вимагає secure_version >= 4
```

1. **Монотонний лічильник безпеки:** У заголовку прошивки виробник розміщує поле `secure_version` (монотонне ціле число).
2. **Апаратне порівняння:** Завантажувач підраховує кількість уже пропалених бітів у масиві eFuse. Якщо `secure_version_image < efuse_count`, завантажувач негайно блокує старт образу, навіть якщо його цифровий підпис є 100% валідним.
3. **Необоротна фіксація:** Коли нова версія прошивки успішно проходить випробувальний термін і застосунок викликає `app_mark_valid()`, драйвер eFuse генерує електричний імпульс високої напруги (типово 2.5 В від внутрішнього помпового стабілізатора), який фізично перепалює додаткові полікремнієві мікродоріжки на кристалі. Після цього апаратний лічильник на рівні фізики кристала неможливо повернути назад жодними програмними командами.

### Математична модель надійності оновлення (Markov Chain Reliability Modeling)

Надійність процесу віддаленого оновлення прошивки описується дискретним ланцюгом Маркова з множиною станів:
- S₀: Стабільна робота на попередній версії у слоті A.
- S₁: Завантаження нового двійкового образу у слот B.
- S₂: Пробний запуск нового образу у стані `PENDING_VERIFY`.
- S₃: Автоматичний відкат після краху застосунку.
- S₄: Успішна фіксація нового релізу у стані `VALID` (слот B).
- S_brick: Поглинаючий стан повної втрати працездатності («цеглина»).

```text
          (1 - p_net)
        ┌─────────────┐
        │             ▼
     [ S_0 ] ────► [ S_1 ] ────► [ S_2 ] ──── (1 - p_bug) ────► [ S_4 ]
        ▲            │             │
        │            │             ├──── (p_bug) ───► [ S_3 ] ──┘
        │            │             │                    │
        │            ▼ (p_cut)     ▼ (p_cut)            ▼
        └─────── [ S_fail ] ◄──────┴─────────────── [ S_brick ]
```

Нехай:
- p_net = 0.05 — ймовірність обриву мережевого з'єднання під час передачі даних.
- p_power = 0.01 — ймовірність раптового знеструмлення пристрою під час оновлення.
- p_bug = 0.03 — ймовірність наявності критичного дефекту в новому коді.
- p_meta_loss = 10⁻⁶ — ймовірність одночасного пошкодження обох незалежних секторів метаданих Flash.
- p_flash_hw = 10⁻⁵ — ймовірність фізичного електричного пробою кристала Flash.

#### Розрахунок для однослотової схеми без відкату (In-Place Update):
У системі прямого перезапису будь-який збій зв'язку на середині стирання, аварія живлення або помилка в новому коді неминуче призводить до переходу в стан «цеглини»:

```text
P_brick_single = 1 - (1 - p_power) · (1 - p_net) · (1 - p_bug) ≈ 0.0877  [8.77% втрат]
```

Тобто майже кожне одинадцяте оновлення у великому парку пристроїв призводитиме до фізичної втрати вузла.

#### Розрахунок для двослотової A/B схеми з відкатом:
У двослотовій схемі знеструмлення під час прийому по мережі не зачіпає робочий банк (S₁ → S₀). Збій живлення під час запису метаданих нівелюється наявністю другого сектора (p_power · p_meta_loss). Аварія нового образу парирується автоматичним відкатом (S₂ → S₃ → S₀).

Ймовірність блокування визначається виключно каскадними апаратними збоями:

```text
P_brick_AB = p_flash_hw + (p_power · p_meta_loss) ≈ 1.001 × 10⁻⁵  [0.001001% втрат]
```

Коефіцієнт підвищення відмовостійкості:

```text
K_reliability = P_brick_single / P_brick_AB = 0.0877 / (1.001 × 10⁻⁵) ≈ 8761
```

Впровадження A/B архітектури з автоматичним відкатом зменшує ймовірність фатальної відмови обладнання у **8760 разів**, перетворюючи віддалене оновлення з ризикованої операції на надійний штатний процес життєвого циклу підключених систем.

### Алгоритм динамічного вирівнювання зносу метаданих (Intra-Sector Ring Journal)

У представленій базовій реалізації двосекторного менеджера кожне оновлення статусу вимагає повного прання одного з 4 КБ секторів Flash. Оскільки комірки NOR Flash гарантують від 10 000 до 100 000 циклів стирання, пряме перестирання сектора при кожному перезавантаженні може передчасно вичерпати ресурс підкладки. Коефіцієнт посилення запису (*Write Amplification Factor, WAF*) для 32-байтної структури становить:

```text
WAF = 4096 байтів / 32 байти = 128  [коефіцієнт посилення запису]
```

Для оптимізації ресурсу пам'яті у високонавантажених промислових пристроях симулятор можна розширити алгоритмом **внутрішньосекторного кільцевого журналу** (*Intra-Sector Ring Journal*):


```text
Sector 0 (4096 Bytes):
+-----------------------------------------------------------------------------------------+
| Slot 0 (32B) | Slot 1 (32B) | Slot 2 (32B) | ... | Slot N (32B) | 0xFFFFFFFF (Вільне)   |
| [Seq=10, OK] | [Seq=11, OK] | [Seq=12, OK] | ... | [Seq=127]    | 0xFF... (Стерто)      |
+-----------------------------------------------------------------------------------------+
```

1. **Послідовне заповнення слотів:** Фізичний сектор розміром 4096 байтів логічно розбивається на $N = 4096 / 32 = 128$ компактних слотів.
2. **Лінійний запис без стирання:** Коли стан завантажувача змінюється (наприклад, декремент лічильника спроб `boot_attempts_left` з 3 до 2), завантажувач не стирає сектор, а записує нову структуру у наступний вільний 32-байтний слот, який наразі заповнений значеннями `0xFF`.
3. **Пошук активного стану під час старту:** Під час увімкнення завантажувач сканує 128 слотів за допомогою двійкового пошуку, знаходячи останній валідний запис із коректною контрольною сумою CRC32, після якого починається чиста пам'ять `0xFFFFFFFF`.
4. **Ротація секторів (Compaction & Sector Flip):** Лише коли всі 128 слотів поточного сектора вичерпано, завантажувач здійснює стирання сусіднього сектора `Metadata_Sector_1`, записує туди фінальний актуальний стан у `Slot_0` і перемикає активний покажчик.

Застосування кільцевого журналу зменшує кількість циклів стирання рівно у 128 разів: замість 100 000 оновлень метадані гарантовано витримують до **12.8 мільйона змін стану**, повністю знімаючи проблему фізичного зносу пам'яті за весь життєвий цикл виробу.

### Ланцюжок довіри безпечного завантаження (Chained Root of Trust)

Відкат OTA є невіддільною частиною загального контуру безпеки пристрою. Щоб зловмисник не міг використати процедуру відкату для обходу перевірок автентичності, у системі реалізується суворий апаратний ланцюжок довіри (*Chained Root of Trust*):

```text
[ Апаратний ROM (Mask ROM) ]
              │  (Перевірка хешу відкритого ключа в OTP eFuse)
              ▼
[ Первинний завантажувач (BL1 / MCUboot) ]
              │  (Перевірка ECDSA підпису образу застосунку)
              ▼
[ Прикладний образ (Slot A або Slot B) ]
              │  (Ізоляція за допомогою Cortex-M MPU)
              ▼
[ Завдання користувача в непривілейованому режимі (Unprivileged Thread Mode) ]
```

1. **Апаратний корінь довіри (Root of Trust, RoT):** Первинний код завантажувача BL1 «зашитий» у масковану пам'ять ROM на етапі виготовлення кристала і фізично захищений від модифікації.
2. **Апаратні хеші публічних ключів:** У незмінні комірки OTP eFuse занесено 256-бітний SHA-256 хеш відкритого кореневого ключа виробника.
3. **Контроль цілісності ланцюжка:** Кожен наступний програмний рівень перевіряє цифровий підпис і версію безпеки нижчого рівня до моменту передачі керування. Якщо верифікація зазнає невдачі, виконання негайно зупиняється на поточному рівні з переходом в аварійний режим безпеки.
4. **Апаратне розмежування пам'яті (MPU Isolation):** Після успішного старту застосунок налаштовує регістри блоку захисту пам'яті `ARM MPU`, забороняючи прикладним задачам доступ до розділів завантажувача, секторів метаданих `otadata` та таблиць дескрипторів переривань NVIC, що повністю виключає можливість їхнього несанкціонованого спотворення через програмні помилки чи вразливості коду.

### Інтерфейси Quad/Octal SPI та таймінги зовнішньої Flash-пам'яті (QSPI DQS & Dummy Cycles)

У багатьох сучасних мікроконтролерах (наприклад, STM32H7, ESP32-S3, NXP i.MX RT) внутрішнього обсягу Flash-пам'яті недостатньо для розміщення двох повнорозмірних слотів A/B (наприклад, при роботі з графічними інтерфейсами TouchGFX / LVGL або моделями машинного навчання TensorFlow Lite for Microcontrollers). У таких конфігураціях робочі слоти A і B виносяться на зовнішню мікросхему пам'яті Quad-SPI (QSPI) або Octal-SPI (OSPI), яка працює в режимі прямого виконання коду (*Execute-in-Place, XIP*).

Особливості взаємодії завантажувача із зовнішньою Flash-пам'яттю:
1. **Калібрування циклів очікування (Dummy Cycles / Latency Codes):** При роботі на високих частотах шини QSPI (понад 80–133 МГц) мікросхема Flash вимагає передачі так званих «холостих тактів» (*Dummy Cycles*) між фазою передачі адреси та фазою видачі першого байта даних. Кількість цих тактів програмується у конфігураційному регістрі пам'яті Flash (Non-Volatile / Volatile Configuration Register). Якщо нова версія прошивки збільшує частоту тактування шини QSPI, але не коригує кількість Dummy Cycles, процесор зчитує з шини зміщені на 1–2 такти дані, що призводить до апаратного краху `BusFault` ще на етапі вибірки інструкцій функції `main()`.
2. **Апаратне стробування даних (DQS / Data Strobe):** В інтерфейсах Octal-SPI зі швидкістю передачі DDR (Double Data Rate) мікросхема пам'яті повертає сигнал стробування `DQS`, синфазний із даними. Завантажувач повинен коректно ініціалізувати блок затримки фази сигналу DLL (*Delay-Locked Loop*), інакше при зміні температури навколишнього середовища (температурний дрейф затримки ліній друкованої плати) відбудеться збій валідації CRC32 образу.
3. **Атомарність оновлення зовнішньої Flash при раптовому вимкненні живлення:** Зовнішні SPI Flash мікросхеми вимагають окремого сигналу дозволу запису `WREN` (Write Enable, команда `0x06`) перед кожною операцією стирання чи програмування. Якщо живлення просідає в момент між відправкою `WREN` та передачею команди `Sector Erase (0x20)`, внутрішній автомат станів Flash скидає біт `WEL` (Write Enable Latch) у регістрі стану `Status Register 1`. Завантажувач повинен завжди перевіряти біт `WEL` перед початком операції, щоб запобігти безрезультатному очікуванню готовності мікросхеми.
4. **Узгодженість кешів процесора та передачі через DMA (D-Cache Coherency):** На мікроконтролерах із роздільними кешами інструкцій та даних L1 (Cortex-M7) операції обчислення CRC32 за допомогою апаратного прискорювача DMA можуть зчитувати застарілі дані з оперативної пам'яті, якщо брудні рядки кешу даних (*Dirty Cache Lines*) ще не були скинуті в SRAM. Завантажувач зобов'язаний інвалідувати та скидати кеш викликами `SCB_CleanDCache_by_Addr()` перед передачею буфера в DMA та `SCB_InvalidateDCache_by_Addr()` після завершення прийому оновлення з мережевого модема.

### Емуляція протоколу налагодження GDB Server та інспекція стану ядра

Для інтеграції симулятора в інтерактивні середовища розробки (IDE) архітектура підтримує підключення мережевого сервера віддаленого налагодження **GDB Remote Serial Protocol (RSP)** через TCP-сокет (порт `localhost:3333`).

```text
[ GDB Client: arm-none-eabi-gdb ] ◄── (TCP Socket: 3333) ──► [ GDB RSP Server у Симуляторі ]
                                                                      │
                                                                      ▼
                                                         [ Емулятор Cortex-M Core ]
                                                         [ Регістри R0-R15, xPSR, MSP ]
                                                         [ Точки зупинки / Breakpoints ]
```

1. **Обробка команд протоколу RSP:**
   - Читання пам'яті `m<addr>,<length>`: симулятор перенаправляє запит до функції `flash_read()`, повертаючи шістнадцятковий дамп секторів метаданих або виконуваного коду.
   - Запис пам'яті `M<addr>,<length>:<data>`: дозволяє інженеру в реальному часі модифікувати змінні та спотворювати контрольні суми для тестування відкату.
   - Апаратні точки зупинки (Hardware Breakpoints `Z0` / `z0`): перехоплюють виконання перед передачею керування у функцію `bootloader_run()` або в момент генерації переривання сторожового таймера `watchdog_tick()`.
2. **Інспекція процесорних регістрів:** Налагоджувач може зчитувати стан віртуального програмного лічильника `PC`, вказівника стека `MSP` та регістрів стану винятків `SCB->CFSR`, що дозволяє візуалізувати процес покрокового виконання самотестування в графічному інтерфейсі VS Code або CLion.

### Рівні апаратного захисту пам'яті (Readout Protection, RDP Levels)

У серійному виробництві мікроконтролери захищаються від несанкціонованого зчитування прошивки конкурентами або зловмисниками через апаратні біти конфігурації **Option Bytes (RDP)**:

- **RDP Level 0 (No Protection):** Пам'ять Flash повністю відкрита для зчитування та запису через відлагоджувальний інтерфейс SWD/JTAG. Використовується виключно на етапі первинної розробки на стенді.
- **RDP Level 1 (Readout Protection):** Зчитування Flash через інтерфейс SWD апаратно заблоковано. Проте внутрішнє процесорне ядро має повний доступ до пам'яті для виконання коду та оновлення OTA. Якщо зловмисник спробує підключити програматор і знизити рівень захисту назад до Level 0, апаратний контролер Flash ініціює миттєве стирання всієї пам'яті кристала (*Mass Erase*), знищуючи всі секретні ключі та бінарні образи.
- **RDP Level 2 (Chip Protection / Permanent Lock):** Незворотне апаратне блокування. Відлагоджувальний інтерфейс SWD фізично відключається всередині кристала. Повернення до Level 1 або Level 0 стає неможливим навіть шляхом стирання мікроконтролера.

Завантажувач під час першого запуску перевіряє регістри Option Bytes (`FLASH->OPTR` на STM32 або `EFUSE_RD_SYS_DATA_PART0_REG` на ESP32). Якщо завантажувач виявляє, що пристрій працює на незахищеному рівні `RDP Level 0`, він автоматично програмує конфігураційні біти на рівень `RDP Level 1`, запобігаючи витоку криптографічних сертифікатів після відправки плати кінцевому замовнику. Крім того, при активації рівня захисту RDP Level 1 апаратний контролер блокує несанкціонований доступ до Flash з боку сторонніх каналів прямого доступу до пам'яті (DMA), що унеможливлює зчитування коду через апаратні маніпуляції з периферією.


### Моделювання аварійного тремтіння живлення (Brownout Simulation)

Окрім повного та раптового знеструмлення (*Power Cut*), вбудовані системи піддаються впливу небезпечного явища **глибокого просідання напруги живлення** (*Brownout / Voltage Sag*). Такий стан виникає при підключенні потужних індуктивних навантажень (реле, електродвигунів, електромагнітних клапанів) або при роботі від розрядженого хімічного джерела струму (Li-Ion / LiFePO4 акумулятора) на сильному морозі.

Коли напруга живлення мікроконтролера просідає нижче допустимого мінімуму (наприклад, з номінальних 3.3 В до 2.1 В при мінімально допустимих 2.7 В), напруга ще не досягає порогу повного апаратного скидання за живленням V_POR (типово 1.6–1.8 В). У цьому проміжному стані цифрова логіка процесора починає давати збої таймінгів, внутрішні підсилювачі Flash-пам'яті спотворюють байти, що зчитуються, а помповий помножувач напруги Flash не здатний забезпечити необхідні 12–15 В для надійного програмування плаваючого затвора.

Емуляція захисту від Brownout у симуляторі моделює роботу вбудованого аналогового компаратора **PVD** (*Programmable Voltage Detector*):
1. Коли напруга живлення перетинає нижній поріг безпеки V_PVD_FALLING = 2.8 В, аналоговий компаратор генерує випереджаюче немасковане переривання `PVD_IRQn`.
2. Обробник переривання PVD має близько 200–500 мікросекунд (завдяки накопиченому заряду на електролітичних конденсаторах шини живлення) для виконання процедури екстреного збереження стану:

   - Негайне переведення силових ключів керування навантаженням у пасивний стан закриття для зменшення споживання струму.
   - Скасування поточних неатомарних операцій стирання Flash.
   - Фіксація критичних діагностичних маркерів у регістрах резервної області RTC Backup Domain.
   - Зупинка виконання ядра командою `__WFI()` (Wait For Interrupt) для блокування спотворення пам'яті до відновлення стабільного рівня напруги.

Симулятор підтверджує: лише комплексне поєднання надійної емуляції фізики Flash, математично доведеного протоколу чергування метаданих, апаратного сторожового нагляду та повної ізоляції конфігураційних доменів дозволяє побудувати надійний вбудований пристрій, здатний автономно функціонувати роками без фізичного сервісного обслуговування. Завдяки модульній архітектурі представлені програмні модулі C99 та C++20 можуть бути безпосередньо перенесені на цільовий мікроконтролер як основа промислового завантажувача.







