#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Переліки для людино-читабельної конфігурації
typedef enum {
    CLK_EXT_CLOCK          = 0x00, // Прямокутний сигнал на XTAL1
    CLK_INT_RC_8MHZ        = 0x02, // Внутрішній RC-генератор 8.0 МГц
    CLK_INT_128KHZ         = 0x04, // Внутрішній низькочастотний 128 кГц
    CLK_EXT_CRYSTAL_LOW    = 0x08, // Кварц низької частоти (0.4 - 0.9 МГц)
    CLK_EXT_CRYSTAL_MED    = 0x0A, // Кварц середньої частоти (0.9 - 3.0 МГц)
    CLK_EXT_CRYSTAL_HIGH   = 0x0F  // Кварц високої частоти (3.0 - 16.0 МГц)
} avr_clock_source_t;

typedef enum {
    SUT_FAST_RISING        = 0x00, // Швидке наростання VCC (14CK + 0ms)
    SUT_STANDARD           = 0x01, // Стандартний старт (14CK + 4.1ms)
    SUT_SLOW_RISING        = 0x02, // Повільне живлення (14CK + 65ms)
    SUT_MAX_CERAMIC        = 0x03  // Максимальна затримка (16K CK + 65ms)
} avr_sut_t;

typedef enum {
    BOD_DISABLED           = 0x07, // Brown-out детектування вимкнено
    BOD_1V8                = 0x06, // Поріг 1.8V (номінал 1.7 - 2.0V)
    BOD_2V7                = 0x05, // Поріг 2.7V (номінал 2.5 - 2.9V)
    BOD_4V3                = 0x04  // Поріг 4.3V (номінал 4.1 - 4.5V)
} avr_bod_level_t;

typedef enum {
    BOOT_SIZE_256_WORDS    = 0x03, // 512 байтів (адреса 0x3F00 / 0x7E00)
    BOOT_SIZE_512_WORDS    = 0x02, // 1024 байти (адреса 0x3E00 / 0x7C00)
    BOOT_SIZE_1024_WORDS   = 0x01, // 2048 байтів (адреса 0x3C00 / 0x7800)
    BOOT_SIZE_2048_WORDS   = 0x00  // 4096 байтів (адреса 0x3800 / 0x7000)
} avr_bootsz_t;

typedef enum {
    LOCK_MODE_1_OPEN       = 0x03, // Відкритий доступ (читання/запис)
    LOCK_MODE_2_NO_PROG    = 0x02, // Заборона запису через ISP
    LOCK_MODE_3_FULL_LOCK  = 0x00  // Повна заборона читання та запису
} avr_lock_mode_t;

// Структура дескриптора мікроконтролера
typedef struct {
    const char* name;
    const char* avrdude_part;
    uint8_t     signature[3];
    bool        has_extended_fuse;
    uint8_t     efuse_unimplemented_mask;
    uint8_t     lock_unimplemented_mask;
} avr_mcu_descriptor_t;

// Структура людино-читабельних параметрів
typedef struct {
    avr_clock_source_t clock_source;
    avr_sut_t          startup_time;
    bool               clock_output_enable;
    bool               divide_clock_by_8;
    
    bool               reset_disable;        // true = Reset перетворено в GPIO (НЕБЕЗПЕЧНО)
    bool               debugwire_enable;     // true = debugWIRE активовано
    bool               spi_prog_enable;      // true = ISP увімкнено (норма true)
    bool               watchdog_always_on;   // true = апаратний WDT
    bool               preserve_eeprom;      // true = збереження EEPROM при Chip Erase
    avr_bootsz_t       bootloader_size;
    bool               boot_reset_vector;    // true = старт із завантажувача
    
    avr_bod_level_t    bod_level;
    avr_lock_mode_t    lock_mode;
    uint8_t            boot_lock_app_bits;   // BLB0[1:0] (0..3)
    uint8_t            boot_lock_boot_bits;  // BLB1[1:0] (0..3)
} avr_human_config_t;

// Структура сирих байтів конфігурації
typedef struct {
    uint8_t lfuse;
    uint8_t hfuse;
    uint8_t efuse;
    uint8_t lock;
} avr_raw_fuses_t;

// Діагностика
typedef enum {
    DIAG_INFO,
    DIAG_WARNING,
    DIAG_CRITICAL_ERROR
} avr_diag_level_t;

typedef struct {
    avr_diag_level_t level;
    char message[160];
} avr_diag_item_t;

typedef struct {
    bool is_valid_and_safe;
    size_t count;
    avr_diag_item_t items[12];
} avr_audit_result_t;

// Таблиця дескрипторів мікроконтролерів
static const avr_mcu_descriptor_t MCU_DATABASE[] = {
    {
        .name = "ATmega328P",
        .avrdude_part = "m328p",
        .signature = {0x1E, 0x95, 0x0F},
        .has_extended_fuse = true,
        .efuse_unimplemented_mask = 0xF8,
        .lock_unimplemented_mask = 0xC0
    },
    {
        .name = "ATmega2560",
        .avrdude_part = "m2560",
        .signature = {0x1E, 0x98, 0x01},
        .has_extended_fuse = true,
        .efuse_unimplemented_mask = 0xF8,
        .lock_unimplemented_mask = 0xC0
    },
    {
        .name = "ATtiny85",
        .avrdude_part = "t85",
        .signature = {0x1E, 0x93, 0x0B},
        .has_extended_fuse = false,
        .efuse_unimplemented_mask = 0xFF,
        .lock_unimplemented_mask = 0xC0
    }
};

// Кодування людино-читабельної конфігурації у сирі байти
avr_raw_fuses_t avr_encode_fuses(const avr_human_config_t* cfg) {
    avr_raw_fuses_t raw;
    
    // 1. Low Fuse
    raw.lfuse = (cfg->divide_clock_by_8 ? 0x00 : 0x80) |
                (cfg->clock_output_enable ? 0x00 : 0x40) |
                ((cfg->startup_time & 0x03) << 4) |
                (cfg->clock_source & 0x0F);
                
    // 2. High Fuse
    raw.hfuse = (cfg->reset_disable ? 0x00 : 0x80) |
                (cfg->debugwire_enable ? 0x00 : 0x40) |
                (cfg->spi_prog_enable ? 0x00 : 0x20) |
                (cfg->watchdog_always_on ? 0x00 : 0x10) |
                (cfg->preserve_eeprom ? 0x00 : 0x08) |
                ((cfg->bootloader_size & 0x03) << 1) |
                (cfg->boot_reset_vector ? 0x00 : 0x01);
                
    // 3. Extended Fuse (з маскуванням нереалізованих розрядів 7..3 як 1)
    raw.efuse = 0xF8 | (cfg->bod_level & 0x07);
    
    // 4. Lock Bits (з маскуванням нереалізованих розрядів 7..6 як 1)
    raw.lock = 0xC0 |
               ((cfg->boot_lock_boot_bits & 0x03) << 4) |
               ((cfg->boot_lock_app_bits & 0x03) << 2) |
               (cfg->lock_mode & 0x03);
               
    return raw;
}

// Декодування сирих байтів у параметри
avr_human_config_t avr_decode_fuses(avr_raw_fuses_t raw) {
    avr_human_config_t cfg;
    memset(&cfg, 0, sizeof(cfg));
    
    // Low
    cfg.divide_clock_by_8   = (raw.lfuse & 0x80) == 0;
    cfg.clock_output_enable = (raw.lfuse & 0x40) == 0;
    cfg.startup_time        = (avr_sut_t)((raw.lfuse >> 4) & 0x03);
    cfg.clock_source        = (avr_clock_source_t)(raw.lfuse & 0x0F);
    
    // High
    cfg.reset_disable       = (raw.hfuse & 0x80) == 0;
    cfg.debugwire_enable    = (raw.hfuse & 0x40) == 0;
    cfg.spi_prog_enable     = (raw.hfuse & 0x20) == 0;
    cfg.watchdog_always_on  = (raw.hfuse & 0x10) == 0;
    cfg.preserve_eeprom     = (raw.hfuse & 0x08) == 0;
    cfg.bootloader_size     = (avr_bootsz_t)((raw.hfuse >> 1) & 0x03);
    cfg.boot_reset_vector   = (raw.hfuse & 0x01) == 0;
    
    // Extended
    cfg.bod_level           = (avr_bod_level_t)(raw.efuse & 0x07);
    
    // Lock
    cfg.lock_mode           = (avr_lock_mode_t)(raw.lock & 0x03);
    cfg.boot_lock_app_bits  = (raw.lock >> 2) & 0x03;
    cfg.boot_lock_boot_bits = (raw.lock >> 4) & 0x03;
    
    return cfg;
}

// Рушій валідації безпеки
avr_audit_result_t avr_validate_fuses(avr_raw_fuses_t raw, bool allow_hvpp_override) {
    avr_audit_result_t res;
    memset(&res, 0, sizeof(res));
    res.is_valid_and_safe = true;
    
    // Перевірка 1: RSTDISBL
    if ((raw.hfuse & 0x80) == 0) {
        if (!allow_hvpp_override) {
            res.is_valid_and_safe = false;
            snprintf(res.items[res.count++].message, sizeof(res.items[0].message),
                     "ФАТАЛЬНО: RSTDISBL запрограмовано (0)! Пін Reset стане GPIO. ISP прошивка буде неможливою без HVPP.");
            res.items[res.count - 1].level = DIAG_CRITICAL_ERROR;
        } else {
            snprintf(res.items[res.count++].message, sizeof(res.items[0].message),
                     "ПОПЕРЕДЖЕННЯ: RSTDISBL активний. Дозволено через прапорець HVPP.");
            res.items[res.count - 1].level = DIAG_WARNING;
        }
    }
    
    // Перевірка 2: SPIEN
    if ((raw.hfuse & 0x20) != 0) {
        res.is_valid_and_safe = false;
        snprintf(res.items[res.count++].message, sizeof(res.items[0].message),
                 "ФАТАЛЬНО: SPIEN стерто (1)! Інтерфейс послідовного ISP програмування повністю заблоковано.");
        res.items[res.count - 1].level = DIAG_CRITICAL_ERROR;
    }
    
    // Перевірка 3: debugWIRE
    if ((raw.hfuse & 0x40) == 0) {
        snprintf(res.items[res.count++].message, sizeof(res.items[0].message),
                 "УВАГА: debugWIRE увімкнено (DWEN=0). Чіп не відповідатиме звичайному ISP програматору.");
        res.items[res.count - 1].level = DIAG_WARNING;
    }
    
    // Перевірка 4: Тактування vs BOD
    uint8_t cksel = raw.lfuse & 0x0F;
    uint8_t bod   = raw.efuse & 0x07;
    if (cksel >= 0x08 && bod == BOD_DISABLED) {
        snprintf(res.items[res.count++].message, sizeof(res.items[0].message),
                 "РИЗИК: Обрано високочастотний кварц, але Brown-out Detector вимкнено. Можливе псування Flash при спаді живлення.");
        res.items[res.count - 1].level = DIAG_WARNING;
    }
    
    // Перевірка 5: Зовнішній генератор
    if (cksel == 0x00) {
        snprintf(res.items[res.count++].message, sizeof(res.items[0].message),
                 "ІНФО: Режим External Clock. Для роботи обов'язковий зовнішній меандр на ніжці XTAL1.");
        res.items[res.count - 1].level = DIAG_INFO;
    }
    
    // Перевірка 6: Lock Bits
    if ((raw.lock & 0x03) != 0x03) {
        snprintf(res.items[res.count++].message, sizeof(res.items[0].message),
                 "ІНФО: Активовано біти блокування пам'яті Lock Bits (0x%02X). Зчитування Flash буде обмежено.", raw.lock);
        res.items[res.count - 1].level = DIAG_INFO;
    }
    
    return res;
}

// Формування рядка виклику для утиліти avrdude
void avr_format_avrdude_cmd(char* out_buf, size_t buf_len, const char* mcu, avr_raw_fuses_t raw) {
    snprintf(out_buf, buf_len,
             "avrdude -c usbasp -p %s -U lfuse:w:0x%02X:m -U hfuse:w:0x%02X:m -U efuse:w:0x%02X:m -U lock:w:0x%02X:m",
             mcu, raw.lfuse, raw.hfuse, raw.efuse, raw.lock);
}
