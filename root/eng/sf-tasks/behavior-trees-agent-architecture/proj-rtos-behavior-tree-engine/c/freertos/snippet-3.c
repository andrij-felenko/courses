#include "FreeRTOS.h"
#include "task.h"
#include <stdio.h>

// Діагностичний макрос для виводу поточного вузла
#define TRACE_NODE(node_id, status) \
    printf("Node %d returned %d at tick %lu\n", node_id, status, xTaskGetTickCount())

NodeStatus NavigateToTarget_Tick(int node_id) {
    NodeStatus status = RUNNING; 
    
    // Вивід стану допомагає побачити, де саме застрягло дерево
    TRACE_NODE(node_id, status);
    return status;
}
