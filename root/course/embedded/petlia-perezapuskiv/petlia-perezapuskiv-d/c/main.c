#include <stdint.h>
#include <stdbool.h>

/* Спрощені базові адреси регістрів STM32 RCC для наочності стандарту CMSIS */
#define RCC_BASE_ADDR        0x40023800U
#define RCC_CSR_OFFSET       0x74U
#define RCC_CSR_REG          (*(volatile uint32_t *)(RCC_BASE_ADDR + RCC_CSR_OFFSET))

#define RCC_CSR_RMVF_BIT     (1U << 24) /* Очищення прапорців скидання */
#define RCC_CSR_BORRSTF_BIT  (1U << 25) /* Прапорець скидання BOR/POR */
#define RCC_CSR_PINRSTF_BIT  (1U << 26) /* Прапорець скидання кнопкою NRST */
#define RCC_CSR_PORRSTF_BIT  (1U << 27) /* Прапорець холодного старту POR */
#define RCC_CSR_SFTRSTF_BIT  (1U << 28) /* Прапорець програмного скидання */
#define RCC_CSR_IWDGRSTF_BIT (1U << 29) /* Прапорець сторожового таймера IWDG */

#define BOOT_MAGIC_TOKEN     0x5A2C9B1EU
#define MAX_BOR_RETRIES      3U

/* Змінні, що зберігаються між перезапусками у неініціалізованій секції SRAM */
__attribute__((section(".noinit"))) static volatile uint32_t s_boot_token;
__attribute__((section(".noinit"))) static volatile uint32_t s_bor_counter;

typedef enum {
    RESET_REASON_UNKNOWN = 0,
    RESET_REASON_COLD_POWER_ON,
    RESET_REASON_BROWNOUT,
    RESET_REASON_EXTERNAL_PIN,
    RESET_REASON_SOFTWARE,
    RESET_REASON_WATCHDOG
} reset_reason_t;

typedef struct {
    reset_reason_t reason;
    uint32_t       bor_consecutive_failures;
    bool           recovery_mode_active;
    uint8_t        max_allowed_pwm_percent;
} power_safety_context_t;

static power_safety_context_t g_power_ctx;

/* 1. Рання ініціалізація та вичитка причини скидання */
void power_supervisor_early_init(void) {
    uint32_t csr_snapshot = RCC_CSR_REG;
    
    /* Негайне очищення прапорців для запобігання накопиченню бітів */
    RCC_CSR_REG |= RCC_CSR_RMVF_BIT;

    /* Перевірка цілісності SRAM пам'яті */
    if (s_boot_token != BOOT_MAGIC_TOKEN) {
        s_boot_token = BOOT_MAGIC_TOKEN;
        s_bor_counter = 0U;
    }

    /* Розбір причини скидання за пріоритетом */
    if (csr_snapshot & RCC_CSR_BORRSTF_BIT) {
        g_power_ctx.reason = RESET_REASON_BROWNOUT;
        s_bor_counter++;
    } else if (csr_snapshot & RCC_CSR_PORRSTF_BIT) {
        g_power_ctx.reason = RESET_REASON_COLD_POWER_ON;
        s_bor_counter = 0U;
    } else if (csr_snapshot & RCC_CSR_IWDGRSTF_BIT) {
        g_power_ctx.reason = RESET_REASON_WATCHDOG;
    } else if (csr_snapshot & RCC_CSR_SFTRSTF_BIT) {
        g_power_ctx.reason = RESET_REASON_SOFTWARE;
    } else if (csr_snapshot & RCC_CSR_PINRSTF_BIT) {
        g_power_ctx.reason = RESET_REASON_EXTERNAL_PIN;
        s_bor_counter = 0U;
    } else {
        g_power_ctx.reason = RESET_REASON_UNKNOWN;
    }

    g_power_ctx.bor_consecutive_failures = s_bor_counter;

    /* Активація захисного режиму при повторних просадках */
    if (g_power_ctx.bor_consecutive_failures >= MAX_BOR_RETRIES) {
        g_power_ctx.recovery_mode_active = true;
        g_power_ctx.max_allowed_pwm_percent = 25U; /* Обмеження потужності 25% */
    } else {
        g_power_ctx.recovery_mode_active = false;
        g_power_ctx.max_allowed_pwm_percent = 100U;
    }
}

/* 2. Імітація плавної подачі живлення на мотор (Soft-Start) */
void actuator_safe_start(uint8_t target_pwm_percent) {
    uint8_t effective_target = target_pwm_percent;
    
    if (g_power_ctx.recovery_mode_active) {
        if (effective_target > g_power_ctx.max_allowed_pwm_percent) {
            effective_target = g_power_ctx.max_allowed_pwm_percent;
        }
    }

    /* Плавний розгін ШІМ із фіксованим кроком (slew-rate control) */
    for (uint8_t current_pwm = 0U; current_pwm <= effective_target; current_pwm += 5U) {
        /* Тут виконується запис у регістр таймера TIMx->CCR1 = current_pwm */
        
        /* Затримка між східцями для обмеження dI/dt */
        for (volatile uint32_t delay = 0; delay < 50000; delay++) {
            __asm__ volatile ("nop");
        }
    }
}

/* 3. Підтвердження стабільності системи після успішного старту */
void power_supervisor_confirm_stability(void) {
    /* Якщо пристрій успішно пропрацював без скидання, знімаємо статус збою */
    s_bor_counter = 0U;
    g_power_ctx.bor_consecutive_failures = 0U;
    g_power_ctx.recovery_mode_active = false;
    g_power_ctx.max_allowed_pwm_percent = 100U;
}
