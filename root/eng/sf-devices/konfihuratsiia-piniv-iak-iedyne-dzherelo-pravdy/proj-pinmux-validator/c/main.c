#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_PORTS       4
#define PINS_PER_PORT   16
#define MAX_DIAGNOSTICS 32

/* Переліки портів і режимів роботи */
typedef enum {
    PORT_A = 0,
    PORT_B = 1,
    PORT_C = 2,
    PORT_D = 3
} port_id_t;

typedef enum {
    MODE_INPUT       = 0,
    MODE_OUTPUT_PP   = 1,
    MODE_OUTPUT_OD   = 2,
    MODE_AF_PP       = 3,
    MODE_AF_OD       = 4,
    MODE_ANALOG      = 5
} pin_driver_mode_t;

typedef enum {
    PULL_NONE = 0,
    PULL_UP   = 1,
    PULL_DOWN = 2
} pin_pull_mode_t;

typedef enum {
    AF_NONE_GPIO = 0,
    AF1_TIM1_2   = 1,
    AF4_I2C1_3   = 4,
    AF5_SPI1_2   = 5,
    AF7_USART1_2 = 7
} af_num_t;

typedef enum {
    DIAG_SEVERITY_INFO    = 0,
    DIAG_SEVERITY_WARNING = 1,
    DIAG_SEVERITY_ERROR   = 2
} diag_severity_t;

/* Опис можливостей кремнієвого піна */
typedef struct {
    uint16_t af_supported_mask; /* Бітова маска (1 << AF_NUM) */
    bool     has_analog;        /* Чи підтримує ADC/DAC */
    bool     is_5v_tolerant;    /* Чи є FT-піном */
} mcu_pin_capability_t;

/* Опис конфігурації піна на платі */
typedef struct {
    port_id_t         port;
    uint8_t           pin;
    pin_driver_mode_t mode;
    pin_pull_mode_t   pull;
    af_num_t          af;
    bool              enable_exti; /* Чи генерує зовнішнє переривання */
    const char*       signal_name;
    const char*       module_owner;
} board_pin_entry_t;

/* Структура діагностичного повідомлення */
typedef struct {
    diag_severity_t severity;
    port_id_t       port;
    uint8_t         pin;
    char            message[128];
} diagnostic_t;

/* Контекст валідатора */
typedef struct {
    mcu_pin_capability_t capabilities[MAX_PORTS][PINS_PER_PORT];
    diagnostic_t         diagnostics[MAX_DIAGNOSTICS];
    size_t               diag_count;
    size_t               error_count;
    size_t               warning_count;
} validator_context_t;

/* Ініціалізація карти можливостей кремнію */
void validator_init_capabilities(validator_context_t* ctx) {
    memset(ctx, 0, sizeof(*ctx));

    /* Налаштування базових можливостей для мікроконтролера STM32F4-подібної серії */
    for (int p = 0; p < MAX_PORTS; ++p) {
        for (int i = 0; i < PINS_PER_PORT; ++i) {
            ctx->capabilities[p][i].af_supported_mask = (1u << AF_NONE_GPIO);
            ctx->capabilities[p][i].has_analog = false;
            ctx->capabilities[p][i].is_5v_tolerant = true;
        }
    }

    /* Порт A: Можливості спеціальних пінів */
    /* PA0: ADC1_IN0, TIM2_CH1 (AF1) */
    ctx->capabilities[PORT_A][0].has_analog = true;
    ctx->capabilities[PORT_A][0].af_supported_mask |= (1u << AF1_TIM1_2);

    /* PA5..PA7: SPI1 (AF5: SCK, MISO, MOSI) */
    ctx->capabilities[PORT_A][5].af_supported_mask |= (1u << AF5_SPI1_2);
    ctx->capabilities[PORT_A][6].af_supported_mask |= (1u << AF5_SPI1_2);
    ctx->capabilities[PORT_A][7].af_supported_mask |= (1u << AF5_SPI1_2);

    /* PA9..PA10: USART1 (AF7: TX, RX) та TIM1 (AF1) */
    ctx->capabilities[PORT_A][9].af_supported_mask  |= (1u << AF7_USART1_2) | (1u << AF1_TIM1_2);
    ctx->capabilities[PORT_A][10].af_supported_mask |= (1u << AF7_USART1_2) | (1u << AF1_TIM1_2);

    /* Порт B: Можливості I2C */
    /* PB6..PB7: I2C1 (AF4: SCL, SDA) */
    ctx->capabilities[PORT_B][6].af_supported_mask |= (1u << AF4_I2C1_3);
    ctx->capabilities[PORT_B][7].af_supported_mask |= (1u << AF4_I2C1_3);

    /* PC13: Кнопка користувача (без AF) */
    ctx->capabilities[PORT_C][13].af_supported_mask = (1u << AF_NONE_GPIO);
}

/* Додавання діагностики */
void validator_add_diag(validator_context_t* ctx, diag_severity_t sev,
                        port_id_t port, uint8_t pin, const char* msg) {
    if (ctx->diag_count < MAX_DIAGNOSTICS) {
        diagnostic_t* d = &ctx->diagnostics[ctx->diag_count++];
        d->severity = sev;
        d->port = port;
        d->pin = pin;
        strncpy(d->message, msg, sizeof(d->message) - 1);
        d->message[sizeof(d->message) - 1] = '\0';
    }
    if (sev == DIAG_SEVERITY_ERROR) ctx->error_count++;
    if (sev == DIAG_SEVERITY_WARNING) ctx->warning_count++;
}

/* Перевірка маніфесту плати */
bool validator_run(validator_context_t* ctx, const board_pin_entry_t* entries, size_t count) {
    /* Таблиця зайнятості для виявлення колізій */
    const board_pin_entry_t* allocated[MAX_PORTS][PINS_PER_PORT] = {0};
    const board_pin_entry_t* exti_owner[PINS_PER_PORT] = {0};

    for (size_t i = 0; i < count; ++i) {
        const board_pin_entry_t* e = &entries[i];

        /* 1. Базова перевірка меж */
        if (e->port >= MAX_PORTS || e->pin >= PINS_PER_PORT) {
            validator_add_diag(ctx, DIAG_SEVERITY_ERROR, e->port, e->pin,
                               "Неприпустимий номер порту або піна");
            continue;
        }

        /* 2. Перевірка множинного володіння (Multiple Ownership) */
        if (allocated[e->port][e->pin] != NULL) {
            const board_pin_entry_t* prev = allocated[e->port][e->pin];
            char buf[128];
            snprintf(buf, sizeof(buf), "Колізія піна: конфлікт між '%s' (%s) та '%s' (%s)",
                     e->signal_name, e->module_owner, prev->signal_name, prev->module_owner);
            validator_add_diag(ctx, DIAG_SEVERITY_ERROR, e->port, e->pin, buf);
        } else {
            allocated[e->port][e->pin] = e;
        }

        /* 3. Перевірка підтримки альтернативної функції (Invalid AF) */
        const mcu_pin_capability_t* cap = &ctx->capabilities[e->port][e->pin];
        if (e->mode == MODE_AF_PP || e->mode == MODE_AF_OD) {
            if (!(cap->af_supported_mask & (1u << e->af))) {
                char buf[128];
                snprintf(buf, sizeof(buf), "Альтернативна функція AF%d не підтримується кремнієм для сигналу '%s'",
                         e->af, e->signal_name);
                validator_add_diag(ctx, DIAG_SEVERITY_ERROR, e->port, e->pin, buf);
            }
        }

        /* 4. Електричні перевірки режиму виходу (I2C Push-Pull check) */
        if (e->af == AF4_I2C1_3 && e->mode == MODE_AF_PP) {
            validator_add_diag(ctx, DIAG_SEVERITY_ERROR, e->port, e->pin,
                               "Шина I2C вимагає відкритого стоку (AF_OD), Push-Pull неприпустимий!");
        }

        /* 5. Перевірка аналогового режиму (Analog + Pull-Up check) */
        if (e->mode == MODE_ANALOG) {
            if (!cap->has_analog) {
                validator_add_diag(ctx, DIAG_SEVERITY_ERROR, e->port, e->pin,
                                   "Пін не підтримує аналоговий режим (відсутній канал ADC/DAC)");
            }
            if (e->pull != PULL_NONE) {
                validator_add_diag(ctx, DIAG_SEVERITY_WARNING, e->port, e->pin,
                                   "Увімкнено підтяжку в аналоговому режимі — виникне похибка вимірювання ADC");
            }
        }

        /* 6. Перевірка плаваючого цифрового входу */
        if (e->mode == MODE_INPUT && e->pull == PULL_NONE) {
            validator_add_diag(ctx, DIAG_SEVERITY_WARNING, e->port, e->pin,
                               "Цифровий вхід без підтяжки (Floating Input) збільшує споживання струму");
        }

        /* 7. Перевірка колізій зовнішніх переривань EXTI */
        if (e->enable_exti) {
            if (exti_owner[e->pin] != NULL) {
                const board_pin_entry_t* prev_exti = exti_owner[e->pin];
                char buf[128];
                snprintf(buf, sizeof(buf), "Конфлікт EXTI%d: пін P%c%d конфліктує з P%c%d ('%s')",
                         e->pin, 'A' + e->port, e->pin,
                         'A' + prev_exti->port, prev_exti->pin, prev_exti->signal_name);
                validator_add_diag(ctx, DIAG_SEVERITY_ERROR, e->port, e->pin, buf);
            } else {
                exti_owner[e->pin] = e;
            }
        }
    }

    return (ctx->error_count == 0);
}

/* Друк звіту валідації */
void validator_print_report(const validator_context_t* ctx) {
    printf("====================================================\n");
    printf("        ЗВІТ ВАЛІДАЦІЇ КОНФІГУРАЦІЇ ПІНІВ ПЛАТИ     \n");
    printf("====================================================\n");

    for (size_t i = 0; i < ctx->diag_count; ++i) {
        const diagnostic_t* d = &ctx->diagnostics[i];
        const char* sev_str = (d->severity == DIAG_SEVERITY_ERROR)   ? "[ПОМИЛКА] " :
                              (d->severity == DIAG_SEVERITY_WARNING) ? "[ЗАСТЕРЕЖЕННЯ] " : "[ІНФО]   ";
        printf("%s P%c%02d: %s\n", sev_str, 'A' + d->port, d->pin, d->message);
    }

    printf("----------------------------------------------------\n");
    printf("Підсумок: %zu помилок, %zu застережень.\n", ctx->error_count, ctx->warning_count);
    if (ctx->error_count == 0) {
        printf("СТАТУС: [УСПІХ] Конфігурація є безпечною та узгодженою.\n");
    } else {
        printf("СТАТУС: [ВІДХИЛЕНО] Знайдено апаратні колізії! Збірку зупинено.\n");
    }
    printf("====================================================\n");
}

int main(void) {
    validator_context_t ctx;
    validator_init_capabilities(&ctx);

    /* Тестовий маніфест плати з навмисними дефектами для перевірки */
    const board_pin_entry_t board_manifest[] = {
        /* Корректний UART1 */
        { PORT_A, 9,  MODE_AF_PP,     PULL_NONE, AF7_USART1_2, false, "DEBUG_UART_TX",  "uart_driver" },
        { PORT_A, 10, MODE_AF_PP,     PULL_UP,   AF7_USART1_2, false, "DEBUG_UART_RX",  "uart_driver" },

        /* ДЕФЕКТ 1: Подвійне призначення піна PA9 */
        { PORT_A, 9,  MODE_OUTPUT_PP, PULL_NONE, AF_NONE_GPIO, false, "STATUS_LED",     "led_driver" },

        /* ДЕФЕКТ 2: Неприпустима альтернативна функція (SPI1_MOSI на PA9) */
        { PORT_A, 9,  MODE_AF_PP,     PULL_NONE, AF5_SPI1_2,   false, "FLASH_SPI_MOSI", "spi_driver" },

        /* ДЕФЕКТ 3: I2C у режимі Push-Pull замість Open-Drain */
        { PORT_B, 6,  MODE_AF_PP,     PULL_UP,   AF4_I2C1_3,   false, "SENSORS_I2C_SCL", "i2c_driver" },
        { PORT_B, 7,  MODE_AF_OD,     PULL_UP,   AF4_I2C1_3,   false, "SENSORS_I2C_SDA", "i2c_driver" },

        /* ДЕФЕКТ 4: Конфлікт переривань EXTI0 (PA0 та PB0) */
        { PORT_A, 0,  MODE_INPUT,     PULL_DOWN, AF_NONE_GPIO, true,  "USER_BUTTON",    "button_drv" },
        { PORT_B, 0,  MODE_INPUT,     PULL_UP,   AF_NONE_GPIO, true,  "ACCEL_INT1",     "sensor_drv" },

        /* ДЕФЕКТ 5: Аналоговий режим з підтяжкою */
        { PORT_A, 0,  MODE_ANALOG,    PULL_UP,   AF_NONE_GPIO, false, "VBAT_SENSE",     "power_mgr" }
    };

    size_t entry_count = sizeof(board_manifest) / sizeof(board_manifest[0]);
    bool ok = validator_run(&ctx, board_manifest, entry_count);
    validator_print_report(&ctx);

    return ok ? 0 : 1;
}
