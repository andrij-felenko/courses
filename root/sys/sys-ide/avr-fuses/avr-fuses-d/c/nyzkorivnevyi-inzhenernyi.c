#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

// Бітові маски байтів конфігурації ATmega328P
#define FUSE_LOW_CKDIV8_MASK    (1U << 7)
#define FUSE_LOW_CKOUT_MASK     (1U << 6)
#define FUSE_LOW_SUT_MASK       (0x3U << 4)
#define FUSE_LOW_CKSEL_MASK     (0x0FU)

#define FUSE_HIGH_RSTDISBL_MASK (1U << 7)
#define FUSE_HIGH_DWEN_MASK     (1U << 6)
#define FUSE_HIGH_SPIEN_MASK    (1U << 5)
#define FUSE_HIGH_WDTON_MASK    (1U << 4)
#define FUSE_HIGH_EESAVE_MASK   (1U << 3)
#define FUSE_HIGH_BOOTSZ_MASK   (0x3U << 1)
#define FUSE_HIGH_BOOTRST_MASK  (1U << 0)

#define FUSE_EXT_BODLEVEL_MASK  (0x07U)

typedef struct {
    uint8_t lfuse;
    uint8_t hfuse;
    uint8_t efuse;
    uint8_t lock;
} avr_fuses_t;

typedef enum {
    SEVERITY_INFO,
    SEVERITY_WARNING,
    SEVERITY_CRITICAL_BRICK_RISK
} fuse_severity_t;

typedef struct {
    fuse_severity_t severity;
    const char* message;
} fuse_issue_t;

typedef struct {
    bool is_safe_for_isp;
    size_t issue_count;
    fuse_issue_t issues[8];
} fuse_audit_report_t;

// Аналізатор безпеки конфігурації фьюзів
fuse_audit_report_t avr_audit_fuses(avr_fuses_t fuses) {
    fuse_audit_report_t report;
    memset(&report, 0, sizeof(report));
    report.is_safe_for_isp = true;

    // 1. Перевірка відключення виводу RESET (RSTDISBL == 0 -> Programmed)
    if ((fuses.hfuse & FUSE_HIGH_RSTDISBL_MASK) == 0) {
        report.is_safe_for_isp = false;
        report.issues[report.issue_count++] = (fuse_issue_t){
            .severity = SEVERITY_CRITICAL_BRICK_RISK,
            .message = "КРИТИЧНО: RSTDISBL запрограмовано! Вивід Reset перетворено на GPIO. ISP-програмування буде повністю заблоковано."
        };
    }

    // 2. Перевірка відключення інтерфейсу ISP (SPIEN == 1 -> Unprogrammed)
    if ((fuses.hfuse & FUSE_HIGH_SPIEN_MASK) != 0) {
        report.is_safe_for_isp = false;
        report.issues[report.issue_count++] = (fuse_issue_t){
            .severity = SEVERITY_CRITICAL_BRICK_RISK,
            .message = "КРИТИЧНО: SPIEN стерто! Послідовний інтерфейс ISP вимкнено. Відновлення можливе лише через HVPP."
        };
    }

    // 3. Перевірка активного режиму debugWIRE (DWEN == 0)
    if ((fuses.hfuse & FUSE_HIGH_DWEN_MASK) == 0) {
        report.issues[report.issue_count++] = (fuse_issue_t){
            .severity = SEVERITY_WARNING,
            .message = "УВАГА: debugWIRE активовано (DWEN=0). Звичайний ISP не відповідатиме, поки debugWIRE не буде програмно зупинено."
        };
    }

    // 4. Перевірка джерела тактування (CKSEL == 0b0000 -> Зовнішній генератор)
    uint8_t cksel = fuses.lfuse & FUSE_LOW_CKSEL_MASK;
    if (cksel == 0x00) {
        report.issues[report.issue_count++] = (fuse_issue_t){
            .severity = SEVERITY_WARNING,
            .message = "УВАГА: Обрано зовнішній тактовий сигнал (External Clock). Чип перестане відповідати без зовнішнього генератора на XTAL1."
        };
    }

    // 5. Перевірка вимкненого Brown-out детектора (BODLEVEL == 0b111)
    if ((fuses.efuse & FUSE_EXT_BODLEVEL_MASK) == 0x07) {
        report.issues[report.issue_count++] = (fuse_issue_t){
            .severity = SEVERITY_WARNING,
            .message = "ПОПЕРЕДЖЕННЯ: Brown-out Detector вимкнено. Ризик спотворення пам'яті Flash/EEPROM при нестабільному живленні."
        };
    }

    return report;
}

// Генератор команд для CLI утиліти AVRDUDE
void avrdude_print_cmd(avr_fuses_t fuses, const char* mcu) {
    printf("avrdude -c usbasp -p %s -U lfuse:w:0x%02X:m -U hfuse:w:0x%02X:m -U efuse:w:0x%02X:m -U lock:w:0x%02X:m\n",
           mcu, fuses.lfuse, fuses.hfuse, fuses.efuse, fuses.lock);
}
