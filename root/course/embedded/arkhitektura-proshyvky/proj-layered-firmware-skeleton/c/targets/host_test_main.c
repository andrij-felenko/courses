// targets/host_test_main.c — стенд для робочої станції розробника.
// Тут немає ні мікроконтролера, ні давача: шина, ніжка й годинник підмінені
// програмними заглушками, а бізнес-логіка виконується та сама, байт у байт.
#undef NDEBUG  // Перевірки мають працювати і в збірці з оптимізацією
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

#include "app/app_telemetry.h"
#include "bsp/bsp_bme280.h"
#include "bsp/bsp_power.h"
#include "hal/hal_gpio.h"
#include "hal/hal_i2c.h"
#include "hal/hal_time.h"
#include "services/event_dispatcher.h"
#include "services/event_queue.h"
#include "services/power_manager.h"

// ---------------------------------------------------------------------------
// Заглушка шини: масив регістрів плюс кероване псування звʼязку
// ---------------------------------------------------------------------------
typedef struct {
    uint8_t registers[256];
    hal_i2c_status_t fault;  // HAL_I2C_OK = шина здорова
    uint32_t reads;
    uint32_t writes;
    bool powered;
} mock_i2c_ctx_t;

static hal_i2c_status_t mock_i2c_read(void* ctx, uint8_t dev_addr, uint8_t reg, uint8_t* data,
                                      size_t len)
{
    mock_i2c_ctx_t* m = (mock_i2c_ctx_t*)ctx;
    if (dev_addr != BSP_BME280_ADDR_PRIMARY) return HAL_I2C_ERR_NACK;
    if (!m->powered) return HAL_I2C_ERR_TIMEOUT;  // Знеструмлений давач мовчить
    if (m->fault != HAL_I2C_OK) return m->fault;

    m->reads++;
    for (size_t i = 0; i < len; ++i) {
        data[i] = m->registers[(reg + i) & 0xFFu];
    }
    return HAL_I2C_OK;
}

static hal_i2c_status_t mock_i2c_write(void* ctx, uint8_t dev_addr, uint8_t reg,
                                       const uint8_t* data, size_t len)
{
    mock_i2c_ctx_t* m = (mock_i2c_ctx_t*)ctx;
    if (dev_addr != BSP_BME280_ADDR_PRIMARY) return HAL_I2C_ERR_NACK;
    if (!m->powered) return HAL_I2C_ERR_TIMEOUT;
    if (m->fault != HAL_I2C_OK) return m->fault;

    m->writes++;
    for (size_t i = 0; i < len; ++i) {
        m->registers[(reg + i) & 0xFFu] = data[i];
    }
    return HAL_I2C_OK;
}

static const hal_i2c_bus_ops_t mock_i2c_ops = {
    .write_reg = mock_i2c_write,
    .read_reg = mock_i2c_read,
};

// ---------------------------------------------------------------------------
// Заглушка ніжки живлення: клацання ключем «ремонтує» уявний давач
// ---------------------------------------------------------------------------
typedef struct {
    mock_i2c_ctx_t* sensor;
    hal_gpio_level_t level;
    uint32_t falling_edges;
} mock_gpio_ctx_t;

static hal_gpio_status_t mock_gpio_write(void* ctx, uint8_t pin, hal_gpio_level_t level)
{
    (void)pin;
    mock_gpio_ctx_t* g = (mock_gpio_ctx_t*)ctx;
    if (g->level == HAL_GPIO_HIGH && level == HAL_GPIO_LOW) {
        g->falling_edges++;
        g->sensor->powered = false;
        // Знеструмлення прибирає завислий стан мікросхеми — заради цього все й затіяно.
        g->sensor->fault = HAL_I2C_OK;
    }
    if (level == HAL_GPIO_HIGH) {
        g->sensor->powered = true;
    }
    g->level = level;
    return HAL_GPIO_OK;
}

static hal_gpio_status_t mock_gpio_read(void* ctx, uint8_t pin, hal_gpio_level_t* out)
{
    (void)pin;
    *out = ((mock_gpio_ctx_t*)ctx)->level;
    return HAL_GPIO_OK;
}

static const hal_gpio_pin_ops_t mock_gpio_ops = {
    .write = mock_gpio_write,
    .read = mock_gpio_read,
};

// ---------------------------------------------------------------------------
// Заглушка годинника: час рухає сам тест, а не кварц
// ---------------------------------------------------------------------------
typedef struct {
    uint32_t now_ms;
} mock_clock_ctx_t;

static uint32_t mock_now_ms(void* ctx) { return ((mock_clock_ctx_t*)ctx)->now_ms; }

static void mock_delay_ms(void* ctx, uint32_t ms) { ((mock_clock_ctx_t*)ctx)->now_ms += ms; }

static const hal_time_ops_t mock_time_ops = {
    .now_ms = mock_now_ms,
    .delay_ms = mock_delay_ms,
};

// ---------------------------------------------------------------------------
// Заповнення уявної мікросхеми: калібрування з довідки Bosch і вибірка на 40 °C
// ---------------------------------------------------------------------------
static void put_u16(mock_i2c_ctx_t* m, uint8_t reg, uint16_t v)
{
    m->registers[reg] = (uint8_t)(v & 0xFFu);
    m->registers[reg + 1u] = (uint8_t)(v >> 8);
}

static void mock_sensor_load(mock_i2c_ctx_t* m)
{
    memset(m, 0, sizeof(*m));
    m->powered = true;
    m->fault = HAL_I2C_OK;
    m->registers[0xD0] = 0x60;  // Ідентифікатор BME280
    m->registers[0xF3] = 0x00;  // Вибірка завершена, NVM перенесено

    put_u16(m, 0x88, 27504u);           // dig_T1
    put_u16(m, 0x8A, (uint16_t)26435);  // dig_T2
    put_u16(m, 0x8C, (uint16_t)-1000);  // dig_T3
    put_u16(m, 0x8E, 36477u);           // dig_P1
    put_u16(m, 0x90, (uint16_t)-10685); // dig_P2
    put_u16(m, 0x92, (uint16_t)3024);   // dig_P3
    put_u16(m, 0x94, (uint16_t)2855);   // dig_P4
    put_u16(m, 0x96, (uint16_t)140);    // dig_P5
    put_u16(m, 0x98, (uint16_t)-7);     // dig_P6
    put_u16(m, 0x9A, (uint16_t)15500);  // dig_P7
    put_u16(m, 0x9C, (uint16_t)-14600); // dig_P8
    put_u16(m, 0x9E, (uint16_t)6000);   // dig_P9

    m->registers[0xA1] = 75u;            // dig_H1
    put_u16(m, 0xE1, (uint16_t)350);     // dig_H2
    m->registers[0xE3] = 0u;             // dig_H3
    m->registers[0xE4] = 0x14;           // dig_H4 старші 8 біт
    m->registers[0xE5] = 0x06;           // молодший півбайт H4, старший — H5
    m->registers[0xE6] = 0x00;           // dig_H5 старші 8 біт
    m->registers[0xE7] = 30u;            // dig_H6

    // Тиск: сирий код АЦП 415148
    m->registers[0xF7] = 0x65;
    m->registers[0xF8] = 0x5A;
    m->registers[0xF9] = 0xC0;
    // Температура: сирий код 567591 → рівно 40.0 °C після компенсації
    m->registers[0xFA] = 0x8A;
    m->registers[0xFB] = 0x92;
    m->registers[0xFC] = 0x70;
    // Вологість: сирий код 31232
    m->registers[0xFD] = 0x7A;
    m->registers[0xFE] = 0x00;
}

// ---------------------------------------------------------------------------
// Стенд: усі шари, зібрані так само, як на реальній платі
// ---------------------------------------------------------------------------
typedef struct {
    mock_i2c_ctx_t i2c;
    mock_gpio_ctx_t gpio;
    mock_clock_ctx_t clock;

    hal_i2c_bus_t bus;
    hal_time_t time;

    bsp_bme280_storage_t sensor_storage;
    bsp_bme280_t* sensor;
    bsp_power_t rail;

    event_queue_t queue;
    event_dispatcher_t dispatcher;
    power_manager_t power;
    app_telemetry_t app;
} bench_t;

static bool bench_reinit_sensor(void* ctx) { return bsp_bme280_reconfigure((bsp_bme280_t*)ctx); }

static void bench_on_recovered(void* ctx) { app_telemetry_notify_recovered((app_telemetry_t*)ctx); }

static void bench_setup(bench_t* b, float threshold_c, uint16_t sample_period_ticks)
{
    memset(b, 0, sizeof(*b));
    mock_sensor_load(&b->i2c);

    b->gpio.sensor = &b->i2c;
    b->gpio.level = HAL_GPIO_HIGH;
    b->clock.now_ms = 0u;

    b->bus.ops = &mock_i2c_ops;
    b->bus.context = &b->i2c;
    b->time.ops = &mock_time_ops;
    b->time.context = &b->clock;

    b->sensor = bsp_bme280_init(&b->sensor_storage, &b->bus, BSP_BME280_ADDR_PRIMARY);
    assert(b->sensor != NULL);

    hal_gpio_pin_t enable_pin = {.ops = &mock_gpio_ops, .context = &b->gpio, .pin = 5u};
    bsp_power_init(&b->rail, enable_pin, b->time, HAL_GPIO_HIGH, 50u, 100u);

    event_queue_init(&b->queue);
    event_dispatcher_init(&b->dispatcher, &b->queue);

    app_telemetry_init(&b->app, b->sensor, &b->queue, threshold_c, sample_period_ticks);
    assert(event_dispatcher_subscribe(&b->dispatcher,
                                      EVENT_MASK(EVT_TIMER_TICK) | EVENT_MASK(EVT_SENSOR_TRIGGER),
                                      app_telemetry_event_handler, &b->app));

    power_manager_init(&b->power, &b->rail, b->time, 1000u);
    power_manager_set_reinit(&b->power, bench_reinit_sensor, b->sensor);
    power_manager_set_recovered(&b->power, bench_on_recovered, &b->app);
    assert(power_manager_attach(&b->power, &b->dispatcher));
}

static void bench_push(bench_t* b, event_type_t type)
{
    event_t evt = {.type = type, .timestamp_ms = b->clock.now_ms, .payload = {.sensor_val = 0.0f}};
    assert(event_queue_push(&b->queue, &evt));
}

// Скільки подій заданого типу лежить у черзі (черга при цьому спорожнюється).
static uint32_t bench_count_and_drain(bench_t* b, event_type_t type, event_t* last)
{
    uint32_t n = 0u;
    event_t evt;
    while (event_queue_pop(&b->queue, &evt)) {
        if (evt.type == type) {
            n++;
            if (last) *last = evt;
        }
    }
    return n;
}

// ---------------------------------------------------------------------------
// Перевірка 1: перевищення порога породжує подію тривоги
// ---------------------------------------------------------------------------
static void test_alert_above_threshold(void)
{
    bench_t b;
    bench_setup(&b, 35.0f, 10u);

    bsp_bme280_data_t data;
    assert(bsp_bme280_read(b.sensor, &data));
    assert(fabsf(data.temperature_c - 40.0f) < 0.5f);
    assert(data.humidity_percent >= 0.0f && data.humidity_percent <= 100.0f);

    bench_push(&b, EVT_SENSOR_TRIGGER);
    assert(event_dispatcher_drain(&b.dispatcher) == 2u);  // Тригер плюс породжена тривога

    assert(b.app.samples_taken == 1u);
    assert(b.app.alerts_raised == 1u);
    printf("  1. тривога: T=%.2f °C, RH=%.1f %%, p=%.1f гПа\n", (double)data.temperature_c,
           (double)data.humidity_percent, (double)data.pressure_hpa);
}

// ---------------------------------------------------------------------------
// Перевірка 2: під порогом тривоги немає
// ---------------------------------------------------------------------------
static void test_no_alert_below_threshold(void)
{
    bench_t b;
    bench_setup(&b, 50.0f, 10u);

    bench_push(&b, EVT_SENSOR_TRIGGER);
    (void)event_dispatcher_drain(&b.dispatcher);

    assert(b.app.samples_taken == 1u);
    assert(b.app.alerts_raised == 0u);
    printf("  2. поріг 50 °C: тривоги немає\n");
}

// ---------------------------------------------------------------------------
// Перевірка 3: період опитування рахується в тиках таймера
// ---------------------------------------------------------------------------
static void test_tick_period(void)
{
    bench_t b;
    bench_setup(&b, 35.0f, 10u);

    for (int i = 0; i < 9; ++i) {
        bench_push(&b, EVT_TIMER_TICK);
        (void)event_dispatcher_drain(&b.dispatcher);
    }
    assert(b.app.samples_taken == 0u);

    bench_push(&b, EVT_TIMER_TICK);
    (void)event_dispatcher_drain(&b.dispatcher);
    assert(b.app.samples_taken == 1u);
    printf("  3. період: вибірка на десятому тику\n");
}

// ---------------------------------------------------------------------------
// Перевірка 4: повне трасування збою шини — від таймауту до перезапуску живлення
// ---------------------------------------------------------------------------
static void test_bus_fault_recovery(void)
{
    bench_t b;
    bench_setup(&b, 35.0f, 1u);

    // Крок 1: лінію SDA притиснуто, HAL віддає таймаут
    b.i2c.fault = HAL_I2C_ERR_TIMEOUT;

    // Крок 2 і 3: дві невдачі мовчазні, третя переповнює терпіння координатора
    bench_push(&b, EVT_SENSOR_TRIGGER);
    (void)event_dispatcher_drain(&b.dispatcher);
    assert(b.app.faults_raised == 0u);

    bench_push(&b, EVT_SENSOR_TRIGGER);
    (void)event_dispatcher_drain(&b.dispatcher);
    assert(b.app.faults_raised == 0u);

    const uint32_t edges_before = b.gpio.falling_edges;
    bench_push(&b, EVT_SENSOR_TRIGGER);
    // Крок 4: диспетчер витягує EVT_SENSOR_FAULT і віддає його службі живлення
    (void)event_dispatcher_drain(&b.dispatcher);

    assert(b.app.faults_raised == 1u);
    assert(b.power.cycles_done == 1u);
    assert(b.gpio.falling_edges == edges_before + 1u);
    assert(b.rail.cycles == 1u);
    assert(b.gpio.level == HAL_GPIO_HIGH);  // Живлення повернуто
    assert(b.i2c.fault == HAL_I2C_OK);      // Давач відпустив шину
    assert(b.app.consecutive_failures == 0u);

    // Після відновлення вузол знову міряє й знову бачить перевищення порога.
    // Знімаємо рівно одну подію, щоб тривога лишилась у черзі на перевірку.
    bench_push(&b, EVT_SENSOR_TRIGGER);
    assert(event_dispatcher_run_once(&b.dispatcher));
    assert(b.app.samples_taken == 1u);

    event_t alert;
    assert(bench_count_and_drain(&b, EVT_ALERT_THRESHOLD, &alert) == 1u);
    assert(fabsf(alert.payload.sensor_val - 40.0f) < 0.5f);
    printf("  4. збій шини: %u скидання живлення, вузол ожив\n", (unsigned)b.power.cycles_done);
}

// ---------------------------------------------------------------------------
// Перевірка 5: переповнена черга відкидає подію, а не псує память
// ---------------------------------------------------------------------------
static void test_queue_overflow(void)
{
    event_queue_t q;
    event_queue_init(&q);

    event_t evt = {.type = EVT_TIMER_TICK, .timestamp_ms = 0u, .payload = {.sensor_val = 0.0f}};
    // Кільце на N комірок вміщає N-1 подію: одна лишається порожньою, щоб
    // «повно» не було не відрізнити від «порожньо».
    for (unsigned i = 0u; i < EVENT_QUEUE_CAPACITY - 1u; ++i) {
        assert(event_queue_push(&q, &evt));
    }
    assert(!event_queue_push(&q, &evt));
    assert(event_queue_dropped(&q) == 1u);
    assert(event_queue_count(&q) == EVENT_QUEUE_CAPACITY - 1u);

    event_t out;
    assert(event_queue_pop(&q, &out));
    assert(out.type == EVT_TIMER_TICK);
    assert(event_queue_push(&q, &evt));  // Місце звільнилось
    printf("  5. переповнення: подію відкинуто, лічильник зріс\n");
}

int main(void)
{
    printf("Хостовий стенд каркаса прошивки (без мікроконтролера й давача):\n");
    test_alert_above_threshold();
    test_no_alert_below_threshold();
    test_tick_period();
    test_bus_fault_recovery();
    test_queue_overflow();
    printf("Усі перевірки пройдено.\n");
    return 0;
}
