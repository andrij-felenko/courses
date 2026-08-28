#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

typedef enum {
    BT_SUCCESS = 0,
    BT_FAILURE,
    BT_RUNNING
} bt_status_t;

typedef struct {
    float battery_voltage;
    float obstacle_distance;
    bool  geofence_breach;
} drone_blackboard_t;

/* Інтерфейс вузла */
typedef struct bt_node {
    bt_status_t (*tick)(struct bt_node *self, drone_blackboard_t *bb);
    void (*halt)(struct bt_node *self, drone_blackboard_t *bb);
} bt_node_t;

/* Умова: перевірка напруги батареї */
bt_status_t condition_low_battery_tick(bt_node_t *self, drone_blackboard_t *bb) {
    (void)self;
    if (bb->battery_voltage < 14.0f) {
        return BT_SUCCESS; /* Загроза активна */
    }
    return BT_FAILURE;
}

/* Дія: аварійна посадка */
bt_status_t action_emergency_land_tick(bt_node_t *self, drone_blackboard_t *bb) {
    (void)self;
    (void)bb;
    /* Видача команди зниження вертикальної швидкості */
    return BT_RUNNING;
}

void action_emergency_land_halt(bt_node_t *self, drone_blackboard_t *bb) {
    (void)self;
    (void)bb;
    /* Скидання уставки зниження */
}

/* Дія: штатний політ за маршрутом */
bt_status_t action_cruise_tick(bt_node_t *self, drone_blackboard_t *bb) {
    (void)self;
    (void)bb;
    /* Розрахунок вектору тяги до наступної точки */
    return BT_RUNNING;
}

void action_cruise_halt(bt_node_t *self, drone_blackboard_t *bb) {
    (void)self;
    (void)bb;
    /* Безпечне гальмування при перериванні польоту */
}
