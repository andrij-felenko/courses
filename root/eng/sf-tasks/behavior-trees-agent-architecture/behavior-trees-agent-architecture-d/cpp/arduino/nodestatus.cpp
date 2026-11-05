#include <Arduino.h>
#include <array>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <freertos/semphr.h>

// Перелічення статусів виконання вузла Дерева Поведінки
enum class NodeStatus {
    Success,
    Failure,
    Running
};

// Базовий абстрактний клас вузла без динамічної пам'яті
class BehaviorNode {
public:
    virtual NodeStatus tick(void* context) = 0;
    virtual void halt() {}
    virtual ~BehaviorNode() = default;
};

// Керуючий вузол Послідовності (Sequence Node)
template <size_t N>
class SequenceNode : public BehaviorNode {
private:
    std::array<BehaviorNode*, N> children;
    size_t currentChild = 0;

public:
    SequenceNode(const std::array<BehaviorNode*, N>& childNodes) : children(childNodes) {}

    NodeStatus tick(void* context) override {
        while (currentChild < N) {
            NodeStatus status = children[currentChild]->tick(context);
            if (status == NodeStatus::Running) {
                return NodeStatus::Running;
            }
            if (status == NodeStatus::Failure) {
                currentChild = 0;
                return NodeStatus::Failure;
            }
            currentChild++;
        }
        currentChild = 0;
        return NodeStatus::Success;
    }

    void halt() override {
        if (currentChild < N) {
            children[currentChild]->halt();
        }
        currentChild = 0;
    }
};

// Вузол умови перевірки датчика
class BatteryCheckNode : public BehaviorNode {
public:
    NodeStatus tick(void* context) override {
        int batteryLevel = analogRead(A0);
        if (batteryLevel > 500) {
            return NodeStatus::Success;
        }
        return NodeStatus::Failure;
    }
};

// Вузол дії приводу
class DriveActionNode : public BehaviorNode {
public:
    NodeStatus tick(void* context) override {
        digitalWrite(LED_BUILTIN, HIGH);
        return NodeStatus::Success;
    }

    void halt() override {
        digitalWrite(LED_BUILTIN, LOW);
    }
};
