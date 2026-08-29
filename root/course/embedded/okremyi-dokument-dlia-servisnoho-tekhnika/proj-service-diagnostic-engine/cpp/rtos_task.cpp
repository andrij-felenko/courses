// rtos_task.cpp — сервісний рушій як окрема низькопріоритетна задача
// FreeRTOS. Тут же лежить реалізація захоплення шини через м'ютекс.
#include <atomic>
#include <cstdint>

#include "hw_port.hpp"
#include "service_engine.hpp"

extern "C" {
#include "FreeRTOS.h"
#include "queue.h"
#include "semphr.h"
#include "task.h"
}

namespace {

constexpr UBaseType_t kRxQueueLength  = 256;
constexpr std::uint32_t kTaskStackWords = 1024;
constexpr TickType_t  kPollPeriod     = pdMS_TO_TICKS(10);

// Конструктор ServiceEngine нічого апаратного не робить, тому глобальний
// об'єкт до main() безпечний; залізо піднімає begin() у srvStart().
ServiceEngine            gEngine;
QueueHandle_t            gRxQueue  = nullptr;
SemaphoreHandle_t        gBusMutex = nullptr;
std::atomic<std::uint32_t> gDroppedBytes{0};

[[noreturn]] void serviceTask(void*)
{
    for (;;) {
        char c{};
        // Спершу вибираємо все, що встигло накопичитись, потім один крок
        // автомата. Порожня черга блокує задачу на kPollPeriod — саме
        // стільки триває пауза між перевірками таймерів.
        while (xQueueReceive(gRxQueue, &c, kPollPeriod) == pdTRUE) {
            gEngine.feedByte(c);
        }
        gEngine.poll();
    }
}

} // namespace

// Пріоритет свідомо нижчий за задачі регулювання: діагностика ніколи не має
// права відсунути керування.
bool srvStart(UBaseType_t priority) noexcept
{
    gRxQueue  = xQueueCreate(kRxQueueLength, sizeof(char));
    gBusMutex = xSemaphoreCreateMutex();
    if (gRxQueue == nullptr || gBusMutex == nullptr) {
        return false;
    }
    gEngine.begin();
    return xTaskCreate(serviceTask, "srv", kTaskStackWords, nullptr, priority, nullptr) == pdPASS;
}

// ISR приймача UART: жодного розбору, лише передача байта в чергу.
extern "C" void srv_uart_rx_isr(char c)
{
    BaseType_t woken = pdFALSE;
    if (xQueueSendFromISR(gRxQueue, &c, &woken) != pdTRUE) {
        gDroppedBytes.fetch_add(1, std::memory_order_relaxed); // рядок піде в брак
    }
    portYIELD_FROM_ISR(woken);
}

// ISR апаратного захисту. Знеструмлення робимо прямо тут, без черги: чекати
// на планувальник, коли горить радіатор, ніхто не буде.
extern "C" void srv_fault_isr(std::uint32_t flags)
{
    gEngine.faultTrip(static_cast<hw::Fault>(flags));
}

// Фіксований тайм-аут замість portMAX_DELAY: сервісний тест радше
// відмовиться від шини, ніж застрягне на ній разом із задачею збору.
bool hw::busTryLock(hw::Millis timeout) noexcept
{
    return gBusMutex != nullptr
           && xSemaphoreTake(gBusMutex, pdMS_TO_TICKS(timeout.count())) == pdTRUE;
}

void hw::busUnlock() noexcept
{
    static_cast<void>(xSemaphoreGive(gBusMutex));
}
