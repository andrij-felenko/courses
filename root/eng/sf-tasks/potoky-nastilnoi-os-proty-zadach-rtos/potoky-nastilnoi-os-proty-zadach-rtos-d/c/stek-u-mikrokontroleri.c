// Виділення статичного буфера під стек задачі у FreeRTOS (C API)
#define CONTROL_TASK_STACK_SIZE 256 // розмір у 32-бітних словах (1024 байти)
static StackType_t xControlTaskStack[CONTROL_TASK_STACK_SIZE];
static StaticTask_t xControlTaskTCB;

TaskHandle_t xHandle = xTaskCreateStatic(
    vControlTaskCode,
    "MotorCtrl",
    CONTROL_TASK_STACK_SIZE,
    NULL,
    configMAX_PRIORITIES - 1,
    xControlTaskStack,
    &xControlTaskTCB
);
