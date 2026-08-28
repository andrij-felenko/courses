/* Контекст локального автономного регулятора на C */
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    MODE_ONLINE_SYNCED,
    MODE_OFFLINE_SOVEREIGN,
    MODE_RECONCILING_DRAIN
} node_network_mode_t;

typedef struct {
    int16_t  target_temp_x10;      /* Цільова уставка */
    int16_t  hysteresis_x10;       /* Зона нечутливості */
    bool     safety_alarm_active;  /* Аварійне блокування */
    bool     actuator_relay_state; /* Поточний стан реле */
    uint32_t state_generation;     /* Покоління локального стану */
} sovereign_node_t;

/* Обчислення керуючого впливу в локальному циклі (без викликів мережі) */
void sovereign_node_step(sovereign_node_t *node, int16_t current_temp_x10) {
    /* 1. Захисний інваріант: перегрів вище 50.0 °C викликає засувку аварії */
    if (current_temp_x10 > 500) {
        node->safety_alarm_active = true;
        node->actuator_relay_state = false;
        node->state_generation++;
        return;
    }

    /* 2. Якщо аварія зафіксована — вихід заборонено */
    if (node->safety_alarm_active) {
        node->actuator_relay_state = false;
        return;
    }

    /* 3. Автономне двопозиційне регулювання з гістерезисом */
    int16_t low_bound  = node->target_temp_x10 - node->hysteresis_x10;
    int16_t high_bound = node->target_temp_x10 + node->hysteresis_x10;

    if (current_temp_x10 < low_bound && !node->actuator_relay_state) {
        node->actuator_relay_state = true;
        node->state_generation++;
    } else if (current_temp_x10 > high_bound && node->actuator_relay_state) {
        node->actuator_relay_state = false;
        node->state_generation++;
    }
}
