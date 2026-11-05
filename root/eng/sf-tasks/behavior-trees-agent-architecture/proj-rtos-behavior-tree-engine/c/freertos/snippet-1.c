#include "FreeRTOS.h"
#include "event_groups.h"

// Група подій для синхронізації датчиків
EventGroupHandle_t sensorEvents;
#define EVENT_OBSTACLE (1 << 0)

// Функція вузла очікування перешкоди
NodeStatus WaitObstacleNode_Tick() {
    // Чекаємо подію не блокуючи весь рушій.
    // Нульовий тайм-аут дозволяє миттєво перевірити стан.
    EventBits_t uxBits = xEventGroupWaitBits(
        sensorEvents, 
        EVENT_OBSTACLE, 
        pdTRUE,  // Очистити біт після зчитування
        pdFALSE, 
        0 
    );

    if ((uxBits & EVENT_OBSTACLE) != 0) {
        return SUCCESS; // Подія настала
    }
    return RUNNING; // Продовжуємо чекати
}
