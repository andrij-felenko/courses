#include "FreeRTOS.h"
#include "event_groups.h"

class WaitObstacleNode : public BehaviorNode {
private:
    EventGroupHandle_t sensorEvents;
    const EventBits_t EVENT_OBSTACLE = (1 << 0);

public:
    WaitObstacleNode(EventGroupHandle_t events) : sensorEvents(events) {}

    NodeStatus tick() override {
        EventBits_t uxBits = xEventGroupWaitBits(
            sensorEvents, 
            EVENT_OBSTACLE, 
            pdTRUE, 
            pdFALSE, 
            0 
        );

        if ((uxBits & EVENT_OBSTACLE) != 0) {
            return NodeStatus::SUCCESS;
        }
        return NodeStatus::RUNNING;
    }
};
