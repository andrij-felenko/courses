#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"

/* Статуси виконання вузла дерева поведінки */
typedef enum {
    BT_STATUS_SUCCESS,
    BT_STATUS_FAILURE,
    BT_STATUS_RUNNING
} bt_status_t;

/* Типи вузлів */
typedef enum {
    BT_NODE_TYPE_ACTION,
    BT_NODE_TYPE_CONDITION,
    BT_NODE_TYPE_SEQUENCE,
    BT_NODE_TYPE_SELECTOR
} bt_node_type_t;

/* Форвард проголошення структури вузла */
struct bt_node;

/* Вказівник на функцію виконання вузла */
typedef bt_status_t (*bt_node_fn)(struct bt_node* self, void* context);

/* Максимальна кількість дітей у керуючому вузлі без використання кучі */
#define BT_MAX_CHILDREN 4

/* Структура вузла Дерева Поведінки */
typedef struct bt_node {
    bt_node_type_t type;
    bt_node_fn execute;
    struct bt_node* children[BT_MAX_CHILDREN];
    uint8_t children_count;
    uint8_t current_running_child;
} bt_node_t;

/* Структура Blackboard для збереження стану агента */
typedef struct {
    uint32_t battery_level;
    bool obstacle_detected;
    SemaphoreHandle_t lock;
} agent_blackboard_t;

/* Реалізація обходу Sequence (Послідовність) */
bt_status_t bt_sequence_execute(bt_node_t* self, void* context) {
    for (uint8_t i = self->current_running_child; i < self->children_count; i++) {
        bt_status_t status = self->children[i]->execute(self->children[i], context);
        if (status == BT_STATUS_RUNNING) {
            self->current_running_child = i;
            return BT_STATUS_RUNNING;
        }
        if (status == BT_STATUS_FAILURE) {
            self->current_running_child = 0;
            return BT_STATUS_FAILURE;
        }
    }
    self->current_running_child = 0;
    return BT_STATUS_SUCCESS;
}

/* Реалізація обходу Selector (Селектор) */
bt_status_t bt_selector_execute(bt_node_t* self, void* context) {
    for (uint8_t i = self->current_running_child; i < self->children_count; i++) {
        bt_status_t status = self->children[i]->execute(self->children[i], context);
        if (status == BT_STATUS_RUNNING) {
            self->current_running_child = i;
            return BT_STATUS_RUNNING;
        }
        if (status == BT_STATUS_SUCCESS) {
            self->current_running_child = 0;
            return BT_STATUS_SUCCESS;
        }
    }
    self->current_running_child = 0;
    return BT_STATUS_FAILURE;
}

/* Приклад Condition node: Перевірка заряду батареї */
bt_status_t condition_check_battery(bt_node_t* self, void* context) {
    agent_blackboard_t* bb = (agent_blackboard_t*)context;
    bool ok = false;
    if (xSemaphoreTake(bb->lock, pdMS_TO_TICKS(10)) == pdTRUE) {
        ok = (bb->battery_level > 20);
        xSemaphoreGive(bb->lock);
    }
    return ok ? BT_STATUS_SUCCESS : BT_STATUS_FAILURE;
}

/* Приклад Action node: Рух вперед */
bt_status_t action_move_forward(bt_node_t* self, void* context) {
    printf("[BT Agent] Рух вперед виконується...\n");
    return BT_STATUS_SUCCESS;
}

/* Основна задача обходу Дерева Поведінки під FreeRTOS */
void bt_agent_task(void* pvParameters) {
    agent_blackboard_t* bb = (agent_blackboard_t*)pvParameters;

    /* Статичне оголошення вузлів дерева без dynamic allocation */
    bt_node_t cond_node = { .type = BT_NODE_TYPE_CONDITION, .execute = condition_check_battery, .children_count = 0 };
    bt_node_t act_node  = { .type = BT_NODE_TYPE_ACTION,    .execute = action_move_forward,     .children_count = 0 };

    bt_node_t root_seq  = {
        .type = BT_NODE_TYPE_SEQUENCE,
        .execute = bt_sequence_execute,
        .children = { &cond_node, &act_node },
        .children_count = 2,
        .current_running_child = 0
    };

    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xFrequency = pdMS_TO_TICKS(100); // 10 Гц тикування

    while (1) {
        /* Запуск виконання тику від кореневого вузла */
        bt_status_t result = root_seq.execute(&root_seq, bb);
        (void)result;

        vTaskDelayUntil(&xLastWakeTime, xFrequency);
    }
}
