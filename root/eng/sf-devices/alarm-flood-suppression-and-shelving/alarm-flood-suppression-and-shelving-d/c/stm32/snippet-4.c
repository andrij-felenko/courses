#include <stdint.h>
#include <stdbool.h>

#define MAX_ALARMS 32U
#define FLIGHT_RECORDER_DEPTH 128U

typedef struct {
    uint32_t timestamp_tick;
    uint32_t raw_vector;
    uint32_t suppress_vector;
    uint32_t final_vector;
    uint8_t  fsm_mode;
} FlightRecord_t;

typedef struct {
    FlightRecord_t records[FLIGHT_RECORDER_DEPTH];
    uint32_t head;
    bool frozen;
} FlightRecorder_t;

static FlightRecorder_t g_flight_recorder;

// Перевірка ациклічності графу (DFS) під час ініціалізації
bool Alarm_Validate_DAG_Acyclic(const uint32_t* adj_matrix, uint32_t count) {
    for (uint32_t i = 0; i < count; i++) {
        uint32_t visited = 0;
        uint32_t stack = (1U << i);

        while (stack != 0U) {
            uint32_t bit_idx = 31U - (uint32_t)__builtin_clz(stack);
            stack &= ~(1U << bit_idx);

            if ((visited & (1U << bit_idx)) != 0U) {
                return false; // Виявлено цикл у графі причинності!
            }
            visited |= (1U << bit_idx);
            stack |= adj_matrix[bit_idx];
        }
    }
    return true;
}

// Розрахунок авто-повернення з урахуванням переповнення системного лічильника
bool Alarm_Check_Shelve_Timeout(uint32_t start_tick, uint32_t current_tick, uint32_t duration_ticks) {
    // Беззнакова різниця захищена від переповнення 32-бітного лічильника
    uint32_t elapsed_ticks = current_tick - start_tick;
    return (elapsed_ticks >= duration_ticks);
}

// Запис стану в бортовий самописець
void FlightRecorder_Log(uint32_t raw, uint32_t suppress, uint32_t final_vec, uint8_t mode, uint32_t tick) {
    if (g_flight_recorder.frozen) {
        return;
    }
    uint32_t idx = g_flight_recorder.head;
    g_flight_recorder.records[idx] = (FlightRecord_t){
        .timestamp_tick = tick,
        .raw_vector = raw,
        .suppress_vector = suppress,
        .final_vector = final_vec,
        .fsm_mode = mode
    };
    g_flight_recorder.head = (idx + 1U) % FLIGHT_RECORDER_DEPTH;
}

// Заморожування самописця при виникненні критичної аварії
void FlightRecorder_FreezeOnEmergency(void) {
    g_flight_recorder.frozen = true;
}
