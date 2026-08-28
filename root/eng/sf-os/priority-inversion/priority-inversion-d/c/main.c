#include "FreeRTOS.h"
#include "semphr.h"
#include "task.h"

static SemaphoreHandle_t lock;   // замок навколо спільного ресурсу
static volatile int shared;      // те, що захищаємо

// ✗ Без успадкування: двійковий семафор.
// Тут можлива НЕОБМЕЖЕНА інверсія.
lock = xSemaphoreCreateBinary();
xSemaphoreGive(lock);            // семафор треба спершу «наповнити»

// ✓ З успадкуванням: справжній м'ютекс.
// Власник тимчасово підніметься до пріоритету того, хто чекає.
lock = xSemaphoreCreateMutex();

// Критична секція — в обох випадках виглядає однаково:
void touch_shared(void) {
    xSemaphoreTake(lock, portMAX_DELAY);   // узяти замок
    shared = compute();                     // ← тут і живе інверсія,
    xSemaphoreGive(lock);                   //   якщо замок «дурний»
}
