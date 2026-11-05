#include "FreeRTOS.h"
#include "task.h"
#include <iostream>

class DebugNode : public BehaviorNode {
private:
    int id;
public:
    DebugNode(int node_id) : id(node_id) {}

    NodeStatus tick() override {
        NodeStatus status = NodeStatus::RUNNING; 
        
        std::cout << "Node " << id << " status: " 
                  << static_cast<int>(status) 
                  << " at tick " << xTaskGetTickCount() << std::endl;
        return status;
    }
};
