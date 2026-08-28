#include <stdint.h>
#include <stdbool.h>

/* Знімок стану датчиків на один крок обчислення */
typedef struct {
    float temperature_c;
    float pressure_bar;
    bool flow_ok;
    bool level_low;
    bool level_high;
    bool e_stop_pressed;
    uint32_t timestamp_ms;
} SensorSnapshot_t;

/* Вектор вихідних команд на виконавчі механізми */
typedef struct {
    bool pump_enable;
    bool heater_enable;
    bool valve_open;
    bool alarm_siren;
} ActuatorCommands_t;

/* Структура подвійного буфера */
typedef struct {
    SensorSnapshot_t buffers[2];
    volatile uint8_t active_idx;
} SnapshotBuffer_t;

static SnapshotBuffer_t g_snapshot_buf;

/* Викликається з ISR після завершення вимірювань */
void Telemetry_CommitSnapshot(const SensorSnapshot_t* fresh_data) {
    uint8_t write_idx = 1 - g_snapshot_buf.active_idx;
    g_snapshot_buf.buffers[write_idx] = *fresh_data;
    g_snapshot_buf.active_idx = write_idx; // Атомарне перемикання покажчика
}

/* Викликається рушієм правил на початку циклу оцінки */
SensorSnapshot_t Telemetry_GetSnapshot(void) {
    return g_snapshot_buf.buffers[g_snapshot_buf.active_idx];
}

/* Чиста функція оцінки правил */
ActuatorCommands_t RuleEngine_Evaluate(const SensorSnapshot_t* in);
