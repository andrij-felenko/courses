#include <stdint.h>
#include <stdbool.h>

typedef void* SemaphoreHandle_t;
extern SemaphoreHandle_t xSemaphoreCreateMutex(void);
extern SemaphoreHandle_t xSemaphoreCreateBinary(void);
extern bool xSemaphoreTake(SemaphoreHandle_t sem, uint32_t timeout);
extern bool xSemaphoreGive(SemaphoreHandle_t sem);
extern bool xSemaphoreGiveFromISR(SemaphoreHandle_t sem, long* pxHigherPriorityTaskWoken);

extern bool hal_spi_transmit_dma_start(const uint8_t* data, uint16_t size);

static SemaphoreHandle_t s_spi_bus_mutex = NULL;     // М'ютекс доступу до шини (з успадкуванням)
static SemaphoreHandle_t s_dma_complete_sem = NULL; // Семафор завершення DMA передачі

void spi_system_init(void)
{
    s_spi_bus_mutex = xSemaphoreCreateMutex();
    s_dma_complete_sem = xSemaphoreCreateBinary();
}

// Захищена атомарна функція передачі великого блоку даних через DMA
bool spi_transfer_dma_safe(const uint8_t* tx_data, uint16_t size, uint32_t timeout_ms)
{
    // 1. Захоплюємо м'ютекс шини (блокує доступ іншим задачам)
    if (!xSemaphoreTake(s_spi_bus_mutex, timeout_ms)) {
        return false; // Тайм-аут очікування звільнення шини
    }

    // 2. Запускаємо апаратну передачу DMA
    if (!hal_spi_transmit_dma_start(tx_data, size)) {
        xSemaphoreGive(s_spi_bus_mutex);
        return false;
    }

    // 3. Блокуємо поточну задачу в очікуванні переривання завершення DMA
    bool dma_ok = xSemaphoreTake(s_dma_complete_sem, timeout_ms);

    // 4. Звільняємо шину для інших задач
    xSemaphoreGive(s_spi_bus_mutex);

    return dma_ok;
}

// Обробник переривання завершення передачі DMA
void DMA1_Channel3_IRQHandler(void)
{
    long higher_prio_woken = 0;
    // Сигналізуємо задачі про закінчення передачі блоку
    xSemaphoreGiveFromISR(s_dma_complete_sem, &higher_prio_woken);
    // Вимагаємо перемикання контексту, якщо розблокована задача має вищий пріоритет
}
