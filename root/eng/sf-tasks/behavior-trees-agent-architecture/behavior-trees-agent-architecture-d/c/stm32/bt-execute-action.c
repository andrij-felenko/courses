#include <stdint.h>
#include <stdbool.h>
#include "stm32f4xx_hal.h"

typedef enum {
    BT_STATUS_FAILURE = 0,
    BT_STATUS_SUCCESS = 1,
    BT_STATUS_RUNNING = 2
} bt_status_t;

typedef enum {
    BT_NODE_SEQUENCE,
    BT_NODE_SELECTOR,
    BT_NODE_ACTION_CHECK_BATTERY,
    BT_NODE_ACTION_MOVE_TO_GOAL
} bt_node_type_t;

typedef struct {
    bt_node_type_t type;
    uint8_t child_start;
    uint8_t child_count;
} bt_node_t;

typedef struct {
    volatile uint16_t battery_level_mv;
    volatile bool obstacle_detected;
} bt_blackboard_t;

#define BT_MAX_NODES 16
#define BT_MAX_DEPTH 8

typedef struct {
    uint8_t node_idx;
    uint8_t current_child;
} bt_stack_frame_t;

static bt_status_t bt_execute_action(bt_node_type_t type, bt_blackboard_t *bb) {
    if (type == BT_NODE_ACTION_CHECK_BATTERY) {
        return (bb->battery_level_mv > 3300) ? BT_STATUS_SUCCESS : BT_STATUS_FAILURE;
    }
    if (type == BT_NODE_ACTION_MOVE_TO_GOAL) {
        if (bb->obstacle_detected) {
            return BT_STATUS_FAILURE;
        }
        return BT_STATUS_RUNNING;
    }
    return BT_STATUS_FAILURE;
}

bt_status_t bt_tick_iterative(const bt_node_t *nodes, uint8_t root_idx, bt_blackboard_t *bb) {
    bt_stack_frame_t stack[BT_MAX_DEPTH];
    int8_t stack_ptr = 0;

    stack[0].node_idx = root_idx;
    stack[0].current_child = 0;

    while (stack_ptr >= 0) {
        bt_stack_frame_t *frame = &stack[stack_ptr];
        const bt_node_t *node = &nodes[frame->node_idx];

        if (node->type == BT_NODE_SEQUENCE) {
            if (frame->current_child >= node->child_count) {
                stack_ptr--;
                if (stack_ptr >= 0) {
                    stack[stack_ptr].current_child++;
                } else {
                    return BT_STATUS_SUCCESS;
                }
                continue;
            }

            uint8_t child_idx = node->child_start + frame->current_child;
            const bt_node_t *child = &nodes[child_idx];

            if (child->type == BT_NODE_SEQUENCE || child->type == BT_NODE_SELECTOR) {
                if (stack_ptr + 1 < BT_MAX_DEPTH) {
                    stack_ptr++;
                    stack[stack_ptr].node_idx = child_idx;
                    stack[stack_ptr].current_child = 0;
                } else {
                    return BT_STATUS_FAILURE;
                }
            } else {
                bt_status_t status = bt_execute_action(child->type, bb);
                if (status == BT_STATUS_FAILURE) {
                    return BT_STATUS_FAILURE;
                }
                if (status == BT_STATUS_RUNNING) {
                    return BT_STATUS_RUNNING;
                }
                frame->current_child++;
            }
        }
    }
    return BT_STATUS_SUCCESS;
}
