#include <string.h>

#include "boot_trigger.h"

/* STM32F4: резервні регістри живуть у домені RTC (RTC_BKP0R = 0x40002850).
   У STM32H7 той самий масив переїхав до блоку TAMP (0x5800B100) — міняється
   лише база, решта логіки та сама. */
#define RCC_BASE          0x40023800u
#define RCC_APB1ENR       (*(volatile uint32_t *)(RCC_BASE + 0x40u))
#define RCC_APB1ENR_PWREN (1u << 28)

#define PWR_BASE   0x40007000u
#define PWR_CR     (*(volatile uint32_t *)(PWR_BASE + 0x00u))
#define PWR_CR_DBP (1u << 8) /* Disable Backup domain write Protection */

#define RTC_BASE   0x40002800u
#define RTC_BKPR(i) (*(volatile uint32_t *)(RTC_BASE + 0x50u + 4u * (uint32_t)(i)))

#define SCB_AIRCR  (*(volatile uint32_t *)0xE000ED0Cu)
#define AIRCR_KEY_SYSRESETREQ 0x05FA0004u

static uint32_t g_line_rate;      /* остання швидкість із SET_LINE_CODING */
static uint8_t  g_dtr;            /* стан лінії DTR */
static uint8_t  g_reboot_pending;
static uint32_t g_reboot_at_ms;

/* Відкриває резервний домен на запис і повертає попередній стан біта DBP. */
static uint32_t backup_write_enable(void)
{
    uint32_t was_open;

    RCC_APB1ENR |= RCC_APB1ENR_PWREN;
    (void)RCC_APB1ENR; /* читання після запису — чекаємо такт шини APB */

    was_open = PWR_CR & PWR_CR_DBP;
    PWR_CR |= PWR_CR_DBP;
    return was_open;
}

static void backup_write_restore(uint32_t was_open)
{
    if (was_open == 0u) {
        PWR_CR &= ~PWR_CR_DBP;
    }
}

void boot_trigger_arm(uint32_t magic)
{
    uint32_t was_open = backup_write_enable();
    RTC_BKPR(0) = magic;
    backup_write_restore(was_open);
}

uint32_t boot_trigger_take(void)
{
    uint32_t value = RTC_BKPR(0);
    uint32_t was_open;

    switch (value) {
    case BOOT_MAGIC_FORCE_BOOTLOADER:
    case BOOT_MAGIC_BETAFLIGHT_DFU:
    case BOOT_MAGIC_USB_TOUCH:
        break;
    default:
        return 0u; /* сміття або чистий регістр — стартуємо застосунок */
    }

    /* Очищаємо ОДРАЗУ: інакше зависання в завантажувачі зациклить вхід
       і плата вже ніколи не дійде до польотного коду. */
    was_open = backup_write_enable();
    RTC_BKPR(0) = 0u;
    backup_write_restore(was_open);
    return value;
}

void boot_trigger_arm_rollback(void)
{
    uint32_t was_open = backup_write_enable();
    RTC_BKPR(1) = BOOT_MAGIC_ROLLBACK;
    backup_write_restore(was_open);
}

int boot_trigger_take_rollback(void)
{
    uint32_t was_open;

    if (RTC_BKPR(1) != BOOT_MAGIC_ROLLBACK) {
        return 0;
    }
    was_open = backup_write_enable();
    RTC_BKPR(1) = 0u;
    backup_write_restore(was_open);
    return 1;
}

void boot_trigger_reset(void)
{
    /* Бар'єр: усі записи в резервний домен мають лягти до скидання. */
    __asm volatile ("dsb 0xF" ::: "memory");
    SCB_AIRCR = AIRCR_KEY_SYSRESETREQ;
    __asm volatile ("dsb 0xF" ::: "memory");
    for (;;) {
        /* Скидання приходить за кілька тактів; сюди керування не повертається. */
    }
}

void boot_trigger_request_reboot(uint32_t magic, uint32_t now_ms)
{
    if (magic != 0u) {
        boot_trigger_arm(magic);
    }
    g_reboot_pending = 1u;
    g_reboot_at_ms = now_ms + BOOT_REBOOT_DELAY_MS;
}

void boot_trigger_service(uint32_t now_ms)
{
    if (g_reboot_pending == 0u) {
        return;
    }
    /* Віднімання зі знаком без знаку коректно переживає переповнення лічильника. */
    if ((int32_t)(now_ms - g_reboot_at_ms) >= 0) {
        boot_trigger_reset();
    }
}

void cdc_set_line_coding(const uint8_t buf[7], uint32_t now_ms)
{
    (void)now_ms;
    if (buf == NULL) {
        return;
    }
    /* dwDTERate — перші чотири байти структури line coding, Little-Endian. */
    g_line_rate = (uint32_t)buf[0]
                | ((uint32_t)buf[1] << 8)
                | ((uint32_t)buf[2] << 16)
                | ((uint32_t)buf[3] << 24);
}

void cdc_set_control_line_state(uint16_t value, uint32_t now_ms)
{
    uint8_t dtr = (uint8_t)(value & 0x1u);
    uint8_t was_dtr = g_dtr;

    g_dtr = dtr;

    /* Магія 1200 bps touch: хост поставив швидкість 1200 і кинув DTR.
       Ловимо саме фронт 1->0, бо драйвер хоста смикає лінію й при відкритті. */
    if (g_line_rate == 1200u && was_dtr != 0u && dtr == 0u) {
        boot_trigger_request_reboot(BOOT_MAGIC_USB_TOUCH, now_ms);
    }
}

void boot_trigger_handle_detach(uint16_t detach_timeout_ms, uint32_t now_ms)
{
    /* bitWillDetach = 1: шину скидаємо самі, чекати на USB Reset від хоста
       не треба, але паузу з wDetachTimeOut поважаємо. */
    uint32_t delay = (detach_timeout_ms < BOOT_REBOOT_DELAY_MS)
                   ? BOOT_REBOOT_DELAY_MS
                   : (uint32_t)detach_timeout_ms;

    boot_trigger_arm(BOOT_MAGIC_FORCE_BOOTLOADER);
    g_reboot_pending = 1u;
    g_reboot_at_ms = now_ms + delay;
}

static float read_float_le(const uint8_t *p)
{
    float value;
    /* memcpy замість розіменування вказівника — жодних припущень
       про вирівнювання буфера прийому. */
    memcpy(&value, p, sizeof value);
    return value;
}

mav_result_t mavlink_handle_command_long(const uint8_t *payload, size_t len,
                                         uint8_t our_system, uint8_t our_component,
                                         uint32_t now_ms)
{
    uint16_t command;
    uint8_t target_system;
    uint8_t target_component;
    float param1;
    int mode;

    if (payload == NULL || len < MAVLINK_COMMAND_LONG_LEN) {
        return MAV_RESULT_FAILED;
    }

    /* Розкладка COMMAND_LONG: 7 float-параметрів, далі command, target_system,
       target_component, confirmation — поля впорядковані за спаданням розміру. */
    command = (uint16_t)((uint16_t)payload[28] | ((uint16_t)payload[29] << 8));
    target_system = payload[30];
    target_component = payload[31];

    if (command != MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN) {
        return MAV_RESULT_UNSUPPORTED;
    }
    if (target_system != 0u && target_system != our_system) {
        return MAV_RESULT_FAILED; /* адресовано іншому борту */
    }
    if (target_component != 0u && target_component != our_component) {
        return MAV_RESULT_FAILED;
    }

    param1 = read_float_le(&payload[0]);
    if (param1 < -0.5f || param1 > 10.0f) {
        return MAV_RESULT_DENIED;
    }
    mode = (int)(param1 + 0.5f); /* по дроту йде float, порівнювати його == не можна */

    switch (mode) {
    case 0:
        return MAV_RESULT_ACCEPTED; /* нічого не робити */
    case 1:
        /* Звичайний перезапуск: маркера не ставимо, стартує польотний код. */
        boot_trigger_request_reboot(0u, now_ms);
        return MAV_RESULT_ACCEPTED;
    case 3:
        boot_trigger_request_reboot(BOOT_MAGIC_FORCE_BOOTLOADER, now_ms);
        return MAV_RESULT_ACCEPTED;
    default:
        /* Вимикання живлення (2) і решту режимів польотний контролер не вміє. */
        return MAV_RESULT_UNSUPPORTED;
    }
}
