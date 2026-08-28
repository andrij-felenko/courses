#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define FRAM_PERSISTENT_ATTR __attribute__((section(".fram_vars")))

#define MAX_TASKS           4
#define SIGNATURE_VALID     0x5AA5C33C
#define VOLTAGE_WARN_PIN    (1 << 3)

typedef struct {
    uint32_t signature;
    uint8_t  current_task_id;
    uint8_t  transaction_epoch;
    uint16_t checksum;
    int32_t  sensor_raw_data[4];
    float    calculated_vibration_rms;
    bool     radio_packet_sent;
} IntermittentCheckpoint_t;

/* Розміщення структур у фероелектричній пам'яті (FRAM) */
static FRAM_PERSISTENT_ATTR IntermittentCheckpoint_t persistent_context_a;
static FRAM_PERSISTENT_ATTR IntermittentCheckpoint_t persistent_context_b;
static FRAM_PERSISTENT_ATTR uint8_t active_context_slot = 0;

static uint16_t calculate_crc(const IntermittentCheckpoint_t *ctx) {
    const uint8_t *data = (const uint8_t *)ctx;
    uint16_t crc = 0xFFFF;
    /* Контрольна сума всього блоку крім поля checksum */
    size_t len = sizeof(IntermittentCheckpoint_t) - sizeof(uint16_t);
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (int j = 0; j < 8; ++j) {
            crc = (crc & 0x8000) ? (crc << 1) ^ 0x1021 : (crc << 1);
        }
    }
    return crc;
}

static IntermittentCheckpoint_t* get_active_context(void) {
    return (active_context_slot == 0) ? &persistent_context_a : &persistent_context_b;
}

static IntermittentCheckpoint_t* get_shadow_context(void) {
    return (active_context_slot == 0) ? &persistent_context_b : &persistent_context_a;
}

/* Атомарна фіксація транзакції у FRAM */
static bool commit_task_transaction(uint8_t next_task_id) {
    IntermittentCheckpoint_t *shadow = get_shadow_context();
    shadow->signature = SIGNATURE_VALID;
    shadow->current_task_id = next_task_id;
    shadow->transaction_epoch++;
    shadow->checksum = calculate_crc(shadow);

    /* Атомарне перемикання активного слота */
    active_context_slot = (active_context_slot == 0) ? 1 : 0;
    return true;
}

/* Апаратна ініціалізація та перевірка цілісності контексту після старту */
void intermittent_system_init(void) {
    IntermittentCheckpoint_t *active = get_active_context();
    if (active->signature != SIGNATURE_VALID || active->checksum != calculate_crc(active)) {
        /* Холодний старт після повної втрати заряду або перший запуск */
        memset(&persistent_context_a, 0, sizeof(IntermittentCheckpoint_t));
        memset(&persistent_context_b, 0, sizeof(IntermittentCheckpoint_t));
        active_context_slot = 0;
        
        active = get_active_context();
        active->signature = SIGNATURE_VALID;
        active->current_task_id = 0;
        active->transaction_epoch = 0;
        active->checksum = calculate_crc(active);
    }
}

/* Приклади атомарних тасок */
static bool task_0_sample_sensor(IntermittentCheckpoint_t *work) {
    /* Симуляція читання 4 осей акселерометра */
    work->sensor_raw_data[0] = 1204;
    work->sensor_raw_data[1] = -450;
    work->sensor_raw_data[2] = 8900;
    work->sensor_raw_data[3] = 34;
    return true;
}

static bool task_1_process_dsp(IntermittentCheckpoint_t *work) {
    int64_t sum_squares = 0;
    for (int i = 0; i < 3; ++i) {
        sum_squares += (int64_t)work->sensor_raw_data[i] * work->sensor_raw_data[i];
    }
    work->calculated_vibration_rms = (float)(sum_squares / 10000);
    return true;
}

static bool task_2_transmit_radio(IntermittentCheckpoint_t *work) {
    /* Передача пакета на частоті 868 МГц */
    work->radio_packet_sent = true;
    return true;
}

/* Головний диспетчер переривчастого виконання */
void intermittent_process_run(void) {
    while (1) {
        IntermittentCheckpoint_t *active = get_active_context();
        IntermittentCheckpoint_t *shadow = get_shadow_context();
        
        /* Клонуємо поточний валідний стан у тіньовий буфер перед роботою */
        memcpy(shadow, active, sizeof(IntermittentCheckpoint_t));
        
        switch (active->current_task_id) {
            case 0:
                if (task_0_sample_sensor(shadow)) {
                    commit_task_transaction(1);
                }
                break;
            case 1:
                if (task_1_process_dsp(shadow)) {
                    commit_task_transaction(2);
                }
                break;
            case 2:
                if (task_2_transmit_radio(shadow)) {
                    commit_task_transaction(3);
                }
                break;
            case 3:
                /* Усі етапи завершено — скидання циклу на новий раунд вимірювань */
                commit_task_transaction(0);
                return;
            default:
                commit_task_transaction(0);
                break;
        }
    }
}
