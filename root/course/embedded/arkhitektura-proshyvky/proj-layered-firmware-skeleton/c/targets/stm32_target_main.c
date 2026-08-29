// targets/stm32_target_main.c — прив'язка каркаса до конкретного чипа.
// ЄДИНЕ місце в проєкті, де згадуються stm32f4xx.h, RCC, I2C1 і номери виводів.
// Замінити STM32F401 на інший контролер означає переписати цей файл — і лише його.
#include "stm32f4xx.h"  // Вендорний CMSIS-заголовок: тільки тут і ніде більше

#include <stddef.h>

#include "app/app_telemetry.h"
#include "bsp/bsp_bme280.h"
#include "bsp/bsp_power.h"
#include "hal/hal_critical.h"
#include "hal/hal_gpio.h"
#include "hal/hal_i2c.h"
#include "hal/hal_time.h"
#include "services/event_dispatcher.h"
#include "services/event_queue.h"
#include "services/power_manager.h"

// --- Розкладка плати -----------------------------------------------------------
#define I2C_SCL_PIN 6u        // PB6, альтернативна функція AF4
#define I2C_SDA_PIN 7u        // PB7, альтернативна функція AF4
#define SENSOR_PWR_PIN 5u     // PB5 → затвор ключа MOSFET лінії давачів
#define PCLK1_HZ 42000000u    // APB1 при ядрі 84 МГц
#define I2C_TIMEOUT_MS 10u    // Ліміт очікування будь-якого прапорця шини
#define TICK_PERIOD_MS 100u   // Крок диспетчерського тику
#define SAMPLE_EVERY_TICKS 10u  // Опитування давача раз на секунду

// --- Годинник на SysTick --------------------------------------------------------
static volatile uint32_t s_uptime_ms = 0u;
static event_queue_t s_queue;  // ISR кладе події сюди

static uint32_t systick_now_ms(void* context)
{
    (void)context;
    return s_uptime_ms;  // 32-бітне читання на Cortex-M неподільне
}

static void systick_delay_ms(void* context, uint32_t ms)
{
    (void)context;
    const uint32_t start = s_uptime_ms;
    while ((uint32_t)(s_uptime_ms - start) < ms) {
        __NOP();
    }
}

static const hal_time_ops_t systick_time_ops = {
    .now_ms = systick_now_ms,
    .delay_ms = systick_delay_ms,
};

void SysTick_Handler(void)
{
    s_uptime_ms++;
    if ((s_uptime_ms % TICK_PERIOD_MS) == 0u) {
        // Подія народжується в перериванні, а обробляється в головному циклі:
        // саме заради цього розриву черга й існує.
        const event_t tick = {
            .type = EVT_TIMER_TICK,
            .timestamp_ms = s_uptime_ms,
            .payload = {.sensor_val = 0.0f},
        };
        (void)event_queue_push(&s_queue, &tick);
    }
}

// --- Ніжка GPIO поверх регістрів порту ------------------------------------------
static hal_gpio_status_t stm32_gpio_write(void* context, uint8_t pin, hal_gpio_level_t level)
{
    GPIO_TypeDef* port = (GPIO_TypeDef*)context;
    if (!port || pin > 15u) return HAL_GPIO_ERR_ARG;
    // BSRR — неподільна установка/скидання без «читати-змінити-записати».
    port->BSRR = (level == HAL_GPIO_HIGH) ? (1u << pin) : (1u << (pin + 16u));
    return HAL_GPIO_OK;
}

static hal_gpio_status_t stm32_gpio_read(void* context, uint8_t pin, hal_gpio_level_t* out_level)
{
    GPIO_TypeDef* port = (GPIO_TypeDef*)context;
    if (!port || pin > 15u) return HAL_GPIO_ERR_ARG;
    *out_level = ((port->IDR & (1u << pin)) != 0u) ? HAL_GPIO_HIGH : HAL_GPIO_LOW;
    return HAL_GPIO_OK;
}

static const hal_gpio_pin_ops_t stm32_gpio_ops = {
    .write = stm32_gpio_write,
    .read = stm32_gpio_read,
};

// --- Шина I2C поверх регістрів контролера ----------------------------------------
typedef struct {
    I2C_TypeDef* i2c;
    hal_time_t time;
    uint32_t timeout_ms;
} stm32_i2c_ctx_t;

static hal_i2c_status_t i2c_abort(stm32_i2c_ctx_t* ctx, hal_i2c_status_t status)
{
    ctx->i2c->CR1 |= I2C_CR1_STOP;
    ctx->i2c->CR1 &= ~(uint32_t)I2C_CR1_POS;
    ctx->i2c->CR1 |= I2C_CR1_ACK;
    return status;
}

// Очікування прапорця з жорстким лімітом часу: зависання в while(!flag)
// перетворює одну несправну мікросхему на несправну прошивку.
static hal_i2c_status_t i2c_wait_sr1(stm32_i2c_ctx_t* ctx, uint32_t mask)
{
    const uint32_t start = hal_time_now_ms(&ctx->time);
    for (;;) {
        const uint32_t sr1 = ctx->i2c->SR1;

        if ((sr1 & I2C_SR1_AF) != 0u) {
            ctx->i2c->SR1 = (uint16_t)~I2C_SR1_AF;
            return i2c_abort(ctx, HAL_I2C_ERR_NACK);
        }
        if ((sr1 & (I2C_SR1_BERR | I2C_SR1_ARLO | I2C_SR1_OVR)) != 0u) {
            ctx->i2c->SR1 = (uint16_t) ~(I2C_SR1_BERR | I2C_SR1_ARLO | I2C_SR1_OVR);
            return i2c_abort(ctx, HAL_I2C_ERR_BUS);
        }
        if ((sr1 & mask) != 0u) {
            return HAL_I2C_OK;
        }
        if (hal_time_elapsed_ms(&ctx->time, start) > ctx->timeout_ms) {
            return i2c_abort(ctx, HAL_I2C_ERR_TIMEOUT);
        }
    }
}

static hal_i2c_status_t i2c_wait_not_busy(stm32_i2c_ctx_t* ctx)
{
    const uint32_t start = hal_time_now_ms(&ctx->time);
    while ((ctx->i2c->SR2 & I2C_SR2_BUSY) != 0u) {
        if (hal_time_elapsed_ms(&ctx->time, start) > ctx->timeout_ms) {
            return HAL_I2C_ERR_BUS;  // Лінію тримає хтось інший — STOP тут не поможе
        }
    }
    return HAL_I2C_OK;
}

static hal_i2c_status_t i2c_start_and_address(stm32_i2c_ctx_t* ctx, uint8_t dev_addr, bool read)
{
    ctx->i2c->CR1 |= I2C_CR1_START;
    hal_i2c_status_t st = i2c_wait_sr1(ctx, I2C_SR1_SB);
    if (st != HAL_I2C_OK) return st;

    ctx->i2c->DR = (uint8_t)((dev_addr << 1) | (read ? 1u : 0u));
    return i2c_wait_sr1(ctx, I2C_SR1_ADDR);
}

// Прапорець ADDR знімається лише парою читань SR1 і SR2 — послідовність із довідника.
static void i2c_clear_addr(stm32_i2c_ctx_t* ctx)
{
    volatile uint32_t tmp = ctx->i2c->SR1;
    tmp = ctx->i2c->SR2;
    (void)tmp;
}

static hal_i2c_status_t stm32_i2c_write_reg(void* context, uint8_t dev_addr, uint8_t reg_addr,
                                            const uint8_t* data, size_t len)
{
    stm32_i2c_ctx_t* ctx = (stm32_i2c_ctx_t*)context;
    if (!ctx || !ctx->i2c) return HAL_I2C_ERR_ARG;

    hal_i2c_status_t st = i2c_wait_not_busy(ctx);
    if (st != HAL_I2C_OK) return st;

    st = i2c_start_and_address(ctx, dev_addr, false);
    if (st != HAL_I2C_OK) return st;
    i2c_clear_addr(ctx);

    st = i2c_wait_sr1(ctx, I2C_SR1_TXE);
    if (st != HAL_I2C_OK) return st;
    ctx->i2c->DR = reg_addr;

    for (size_t i = 0; i < len; ++i) {
        st = i2c_wait_sr1(ctx, I2C_SR1_TXE);
        if (st != HAL_I2C_OK) return st;
        ctx->i2c->DR = data[i];
    }

    st = i2c_wait_sr1(ctx, I2C_SR1_BTF);
    if (st != HAL_I2C_OK) return st;

    ctx->i2c->CR1 |= I2C_CR1_STOP;
    return HAL_I2C_OK;
}

static hal_i2c_status_t stm32_i2c_read_reg(void* context, uint8_t dev_addr, uint8_t reg_addr,
                                           uint8_t* data, size_t len)
{
    stm32_i2c_ctx_t* ctx = (stm32_i2c_ctx_t*)context;
    if (!ctx || !ctx->i2c || len == 0u) return HAL_I2C_ERR_ARG;

    hal_i2c_status_t st = i2c_wait_not_busy(ctx);
    if (st != HAL_I2C_OK) return st;

    // Фаза запису: назвати мікросхемі адресу регістра
    st = i2c_start_and_address(ctx, dev_addr, false);
    if (st != HAL_I2C_OK) return st;
    i2c_clear_addr(ctx);

    st = i2c_wait_sr1(ctx, I2C_SR1_TXE);
    if (st != HAL_I2C_OK) return st;
    ctx->i2c->DR = reg_addr;

    st = i2c_wait_sr1(ctx, I2C_SR1_BTF);
    if (st != HAL_I2C_OK) return st;

    // Фаза читання: повторний старт без відпускання шини
    size_t remaining = len;
    size_t idx = 0u;

    if (remaining == 1u) {
        ctx->i2c->CR1 &= ~(uint32_t)I2C_CR1_ACK;
        st = i2c_start_and_address(ctx, dev_addr, true);
        if (st != HAL_I2C_OK) return st;

        const hal_critical_state_t cs = hal_critical_enter();
        i2c_clear_addr(ctx);
        ctx->i2c->CR1 |= I2C_CR1_STOP;
        hal_critical_exit(cs);

        st = i2c_wait_sr1(ctx, I2C_SR1_RXNE);
        if (st != HAL_I2C_OK) return st;
        data[idx] = (uint8_t)ctx->i2c->DR;
    } else if (remaining == 2u) {
        // Для рівно двох байтів довідник вимагає прапорця POS: NACK готується
        // на другий байт іще до того, як прийшов перший.
        ctx->i2c->CR1 |= I2C_CR1_ACK | I2C_CR1_POS;
        st = i2c_start_and_address(ctx, dev_addr, true);
        if (st != HAL_I2C_OK) return st;

        const hal_critical_state_t cs = hal_critical_enter();
        i2c_clear_addr(ctx);
        ctx->i2c->CR1 &= ~(uint32_t)I2C_CR1_ACK;
        hal_critical_exit(cs);

        st = i2c_wait_sr1(ctx, I2C_SR1_BTF);
        if (st != HAL_I2C_OK) return st;

        const hal_critical_state_t cs2 = hal_critical_enter();
        ctx->i2c->CR1 |= I2C_CR1_STOP;
        data[idx++] = (uint8_t)ctx->i2c->DR;
        hal_critical_exit(cs2);
        data[idx] = (uint8_t)ctx->i2c->DR;

        ctx->i2c->CR1 &= ~(uint32_t)I2C_CR1_POS;
    } else {
        ctx->i2c->CR1 |= I2C_CR1_ACK;
        st = i2c_start_and_address(ctx, dev_addr, true);
        if (st != HAL_I2C_OK) return st;
        i2c_clear_addr(ctx);

        while (remaining > 3u) {
            st = i2c_wait_sr1(ctx, I2C_SR1_RXNE);
            if (st != HAL_I2C_OK) return st;
            data[idx++] = (uint8_t)ctx->i2c->DR;
            remaining--;
        }

        // Лишилось три байти: зняти ACK треба рівно тут, інакше мікросхема
        // почне четвертий і зіпсує кадр.
        st = i2c_wait_sr1(ctx, I2C_SR1_BTF);
        if (st != HAL_I2C_OK) return st;
        ctx->i2c->CR1 &= ~(uint32_t)I2C_CR1_ACK;

        const hal_critical_state_t cs = hal_critical_enter();
        data[idx++] = (uint8_t)ctx->i2c->DR;
        ctx->i2c->CR1 |= I2C_CR1_STOP;
        data[idx++] = (uint8_t)ctx->i2c->DR;
        hal_critical_exit(cs);

        st = i2c_wait_sr1(ctx, I2C_SR1_RXNE);
        if (st != HAL_I2C_OK) return st;
        data[idx] = (uint8_t)ctx->i2c->DR;
    }

    // Дочекатись завершення STOP і повернути ACK для наступної передачі.
    const uint32_t start = hal_time_now_ms(&ctx->time);
    while ((ctx->i2c->CR1 & I2C_CR1_STOP) != 0u) {
        if (hal_time_elapsed_ms(&ctx->time, start) > ctx->timeout_ms) {
            return HAL_I2C_ERR_TIMEOUT;
        }
    }
    ctx->i2c->CR1 |= I2C_CR1_ACK;
    return HAL_I2C_OK;
}

static const hal_i2c_bus_ops_t stm32_i2c_ops = {
    .write_reg = stm32_i2c_write_reg,
    .read_reg = stm32_i2c_read_reg,
};

// --- Ініціалізація периферії -----------------------------------------------------
static void board_clocks_init(void)
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOBEN;
    RCC->APB1ENR |= RCC_APB1ENR_I2C1EN;
    (void)RCC->APB1ENR;  // Затримка на такт шини після ввімкнення тактування
}

static void board_gpio_init(void)
{
    // PB6, PB7 — альтернативна функція AF4, відкритий стік, підтяжка вгору
    GPIOB->MODER &= ~((3u << (I2C_SCL_PIN * 2u)) | (3u << (I2C_SDA_PIN * 2u)));
    GPIOB->MODER |= (2u << (I2C_SCL_PIN * 2u)) | (2u << (I2C_SDA_PIN * 2u));
    GPIOB->OTYPER |= (1u << I2C_SCL_PIN) | (1u << I2C_SDA_PIN);
    GPIOB->OSPEEDR |= (3u << (I2C_SCL_PIN * 2u)) | (3u << (I2C_SDA_PIN * 2u));
    GPIOB->PUPDR &= ~((3u << (I2C_SCL_PIN * 2u)) | (3u << (I2C_SDA_PIN * 2u)));
    GPIOB->PUPDR |= (1u << (I2C_SCL_PIN * 2u)) | (1u << (I2C_SDA_PIN * 2u));
    GPIOB->AFR[0] &= ~((0xFu << (I2C_SCL_PIN * 4u)) | (0xFu << (I2C_SDA_PIN * 4u)));
    GPIOB->AFR[0] |= (4u << (I2C_SCL_PIN * 4u)) | (4u << (I2C_SDA_PIN * 4u));

    // PB5 — звичайний вихід на затвор ключа живлення давачів
    GPIOB->MODER &= ~(3u << (SENSOR_PWR_PIN * 2u));
    GPIOB->MODER |= (1u << (SENSOR_PWR_PIN * 2u));
    GPIOB->OTYPER &= ~(1u << SENSOR_PWR_PIN);
    GPIOB->BSRR = (1u << SENSOR_PWR_PIN);  // Живлення давачів увімкнено
}

static void board_i2c_init(void)
{
    I2C1->CR1 |= I2C_CR1_SWRST;  // Скидання логіки контролера після можливого зависання
    I2C1->CR1 &= ~(uint32_t)I2C_CR1_SWRST;

    I2C1->CR2 = PCLK1_HZ / 1000000u;                  // FREQ у мегагерцах
    I2C1->CCR = (uint16_t)(PCLK1_HZ / (2u * 100000u)); // Стандартний режим 100 кГц
    I2C1->TRISE = (uint16_t)(PCLK1_HZ / 1000000u + 1u);
    I2C1->CR1 |= I2C_CR1_PE | I2C_CR1_ACK;
}

// --- Зшивання шарів --------------------------------------------------------------
// Дескриптор давача може не зʼявитися на холодному старті, тому служба живлення
// дістає не сам дескриптор, а все потрібне, щоб виготовити його з другої спроби.
typedef struct {
    bsp_bme280_storage_t* storage;
    hal_i2c_bus_t* bus;
    bsp_bme280_t** slot;
    app_telemetry_t* app;
} target_sensor_ctx_t;

static bool target_reinit_sensor(void* ctx)
{
    target_sensor_ctx_t* s = (target_sensor_ctx_t*)ctx;

    if (*s->slot) {
        return bsp_bme280_reconfigure(*s->slot);
    }

    *s->slot = bsp_bme280_init(s->storage, s->bus, BSP_BME280_ADDR_PRIMARY);
    if (!*s->slot) {
        return false;
    }
    app_telemetry_set_sensor(s->app, *s->slot);
    return true;
}

static void target_on_recovered(void* ctx) { app_telemetry_notify_recovered((app_telemetry_t*)ctx); }

int main(void)
{
    SystemCoreClockUpdate();
    board_clocks_init();
    board_gpio_init();
    board_i2c_init();

    event_queue_init(&s_queue);
    SysTick_Config(SystemCoreClock / 1000u);  // Тик щомілісекунди

    static hal_time_t time;
    time.ops = &systick_time_ops;
    time.context = NULL;

    static stm32_i2c_ctx_t i2c_ctx;
    i2c_ctx.i2c = I2C1;
    i2c_ctx.time = time;
    i2c_ctx.timeout_ms = I2C_TIMEOUT_MS;

    static hal_i2c_bus_t bus;
    bus.ops = &stm32_i2c_ops;
    bus.context = &i2c_ctx;

    static bsp_bme280_storage_t sensor_storage;
    bsp_bme280_t* sensor = bsp_bme280_init(&sensor_storage, &bus, BSP_BME280_ADDR_PRIMARY);

    static bsp_power_t rail;
    const hal_gpio_pin_t pwr_pin = {
        .ops = &stm32_gpio_ops,
        .context = GPIOB,
        .pin = SENSOR_PWR_PIN,
    };
    bsp_power_init(&rail, pwr_pin, time, HAL_GPIO_HIGH, 50u, 100u);

    if (!sensor) {
        // Давач не озвався на холодному старті: одне скидання живлення й друга спроба.
        (void)bsp_power_cycle_sensors(&rail);
        sensor = bsp_bme280_init(&sensor_storage, &bus, BSP_BME280_ADDR_PRIMARY);
    }

    static event_dispatcher_t dispatcher;
    event_dispatcher_init(&dispatcher, &s_queue);

    static app_telemetry_t app;
    app_telemetry_init(&app, sensor, &s_queue, 35.0f, SAMPLE_EVERY_TICKS);
    (void)event_dispatcher_subscribe(&dispatcher,
                                     EVENT_MASK(EVT_TIMER_TICK) | EVENT_MASK(EVT_SENSOR_TRIGGER),
                                     app_telemetry_event_handler, &app);

    static target_sensor_ctx_t sensor_ctx;
    sensor_ctx.storage = &sensor_storage;
    sensor_ctx.bus = &bus;
    sensor_ctx.slot = &sensor;
    sensor_ctx.app = &app;

    static power_manager_t power;
    power_manager_init(&power, &rail, time, 5000u);
    power_manager_set_reinit(&power, target_reinit_sensor, &sensor_ctx);
    power_manager_set_recovered(&power, target_on_recovered, &app);
    (void)power_manager_attach(&power, &dispatcher);

    for (;;) {
        // Головний цикл нічого не рахує сам: він лише крутить диспетчер.
        if (event_dispatcher_drain(&dispatcher) == 0u) {
            __WFI();  // Черга порожня — спимо до найближчого переривання
        }
    }
}
