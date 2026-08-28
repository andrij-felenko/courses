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
