#include <cstdint>
#include <array>
#include <atomic>
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

// Коди станів вузлів дерева поведінки
enum class NodeStatus : uint8_t {
    FAILURE = 0,
    SUCCESS = 1,
    RUNNING = 2
};

// Типи вузлів для статичної диспетчеризації
enum class NodeType : uint8_t {
    SEQUENCE,
    SELECTOR,
    ACTION_CHECK_BATTERY,
    ACTION_MOVE_TO_GOAL
};

// Структура вузла у пласкому масиві (без динамічних вказівників)
struct BTNode {
    NodeType type;
    uint8_t child_start;
    uint8_t child_count;
};

// Дошка даних (Blackboard) із потокобезпечним доступом
struct Blackboard {
    std::atomic<uint16_t> battery_level_mv{4200};
    std::atomic<bool> obstacle_detected{false};
    SemaphoreHandle_t mutex;

    void init() {
        mutex = xSemaphoreCreateMutex();
    }
};

static constexpr size_t MAX_NODES = 16;
static constexpr size_t MAX_DEPTH = 8;

class BehaviorTreeEngine {
private:
    std::array<BTNode, MAX_NODES> nodes_;
    Blackboard& blackboard_;

    NodeStatus execute_action(NodeType type) {
        if (type == NodeType::ACTION_CHECK_BATTERY) {
            return (blackboard_.battery_level_mv.load() > 3300) 
                   ? NodeStatus::SUCCESS 
                   : NodeStatus::FAILURE;
        }
        if (type == NodeType::ACTION_MOVE_TO_GOAL) {
            if (blackboard_.obstacle_detected.load()) {
                return NodeStatus::FAILURE;
            }
            return NodeStatus::RUNNING;
        }
        return NodeStatus::FAILURE;
    }

public:
    BehaviorTreeEngine(const std::array<BTNode, MAX_NODES>& nodes, Blackboard& bb)
        : nodes_(nodes), blackboard_(bb) {}

    // Ітеративний обхід дерева без рекурсії
    NodeStatus tick(uint8_t root_idx) {
        struct StackFrame {
            uint8_t node_idx;
            uint8_t current_child;
        };

        StackFrame eval_stack[MAX_DEPTH];
        int8_t stack_ptr = 0;

        eval_stack[0] = {root_idx, 0};

        while (stack_ptr >= 0) {
            StackFrame& frame = eval_stack[stack_ptr];
            const BTNode& node = nodes_[frame.node_idx];

            if (node.type == NodeType::SEQUENCE) {
                if (frame.current_child >= node.child_count) {
                    stack_ptr--;
                    if (stack_ptr >= 0) {
                        eval_stack[stack_ptr].current_child++;
                    } else {
                        return NodeStatus::SUCCESS;
                    }
                    continue;
                }

                uint8_t child_idx = node.child_start + frame.current_child;
                const BTNode& child = nodes_[child_idx];

                if (child.type == NodeType::SEQUENCE || child.type == NodeType::SELECTOR) {
                    if (stack_ptr + 1 < static_cast<int8_t>(MAX_DEPTH)) {
                        stack_ptr++;
                        eval_stack[stack_ptr] = {child_idx, 0};
                    } else {
                        return NodeStatus::FAILURE;
                    }
                } else {
                    NodeStatus status = execute_action(child.type);
                    if (status == NodeStatus::FAILURE) {
                        return NodeStatus::FAILURE;
                    }
                    if (status == NodeStatus::RUNNING) {
                        return NodeStatus::RUNNING;
                    }
                    frame.current_child++;
                }
            }
        }
        return NodeStatus::SUCCESS;
    }
};
