// app/app_telemetry.h — чиста бізнес-політика вузла телеметрії.
// Не знає ні про I2C1, ні про ніжку MOSFET: бачить лише драйвер давача й чергу подій.
#ifndef APP_TELEMETRY_H
#define APP_TELEMETRY_H

#include "bsp/bsp_bme280.h"
#include "services/event_queue.h"

// Скільки невдалих опитувань поспіль дозволено, перш ніж вузол оголосить давач несправним.
#define APP_SENSOR_FAULT_LIMIT 3u

typedef struct {
    bsp_bme280_t* sensor;
    event_queue_t* queue;
    float alert_threshold_c;

    uint16_t sample_period_ticks;  // Скільки тиків таймера між опитуваннями
    uint16_t ticks_since_sample;
    uint8_t consecutive_failures;

    bool has_last_reading;
    bsp_bme280_data_t last_reading;

    uint32_t samples_taken;
    uint32_t alerts_raised;
    uint32_t faults_raised;
} app_telemetry_t;

void app_telemetry_init(app_telemetry_t* app, bsp_bme280_t* sensor, event_queue_t* queue,
                        float threshold_c, uint16_t sample_period_ticks);

// Єдина точка входу бізнес-логіки. Тик таймера накопичує період, тригер опитує давач
// негайно; решта типів подій цього координатора не обходить.
void app_telemetry_process_event(app_telemetry_t* app, const event_t* evt);

// Перехідник під таблицю підписників диспетчера.
void app_telemetry_event_handler(void* context, const event_t* evt);

// Дескриптор давача зʼявляється не завжди одразу: на холодному старті шина може
// мовчати. Доки його немає, опитування рахується невдалим — і звичайний шлях
// «три невдачі → несправність → скидання живлення» сам піднімає давач.
void app_telemetry_set_sensor(app_telemetry_t* app, bsp_bme280_t* sensor);

// Після успішного перезапуску живлення лічильник відмов треба обнулити,
// інакше наступна ж невдача одразу дасть нову тривогу.
void app_telemetry_notify_recovered(app_telemetry_t* app);

bool app_telemetry_last_reading(const app_telemetry_t* app, bsp_bme280_data_t* out);

#endif  // APP_TELEMETRY_H
