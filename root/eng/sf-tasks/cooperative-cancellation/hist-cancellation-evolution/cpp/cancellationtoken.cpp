#include <atomic>
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

// Структура маркера скасування для вбудованих систем
struct CancellationToken {
    std::atomic<bool> is_cancelled{false};
    
    void request_cancel() noexcept {
        is_cancelled.store(true, std::memory_order_release);
    }
    
    bool is_cancellation_requested() const noexcept {
        return is_cancelled.load(std::memory_order_acquire);
    }
};

// Функція зупинки периферії та очищення буферів
void stop_dma_hardware_transfer() {
    // Скидання прапорців та вимкнення каналу DMA у вихідний стан
    DMA1_Channel1->CCR &= ~DMA_CCR_EN;
    while ((DMA1_Channel1->CCR & DMA_CCR_EN) != 0) {
        // Очікування апаратного зупинення каналу
    }
}

// Робоча задача обробки сигналів
void sensor_processing_task(void* pvParameters) {
    auto* token = static_cast<CancellationToken*>(pvParameters);
    
    while (true) {
        // Точка скасування перед початком нової ітерації
        if (token->is_cancellation_requested()) {
            // Безпечне зупинення апаратних модулів
            stop_dma_hardware_transfer();
            
            // Звільнення ресурсів та завершення задачі RTOS
            vTaskDelete(NULL);
            return;
        }
        
        // Основне обчислювальне навантаження прошивки
        process_next_sensor_block();
    }
}
