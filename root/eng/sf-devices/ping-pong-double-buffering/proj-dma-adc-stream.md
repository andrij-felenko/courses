# Проект: Подвійна буферизація DMA ADC (Ping-Pong Buffering)

У реальному часі обробка цифрових сигналів з аналогово-цифрового перетворювача (АЦП) вимагає безперервного зчитування даних без втрати відліків та без виклику надмірної кількості переривань процесора. Стандартне одинарне буферування створює стан гонки (race condition): якщо центральний процесор (ЦПУ) читає буфер у той самий момент, коли DMA модуль записує до нього нові відліки АЦП, виникає спотворення даних.

Режимом розв'язання цієї проблеми є **подвійна буферизація (Ping-Pong Buffering)** за допомогою прямого доступу до пам'яті (DMA) у кільцевому (Circular) режимі.

---

## 1. Принцип роботи Ping-Pong буферизації

Пам'ять розбивається на єдиний неперервний масив із $2N$ відліків, який логічно ділиться на два однакові блоки по $N$ елементів:
- **Буфер A (Ping)**: Елементи від `0` до `N - 1`.
- **Буфер B (Pong)**: Елементи від `N` до `2N - 1`.

```
Масив у пам'яті: [ --------- Буфер A (Ping) --------- | --------- Буфер B (Pong) --------- ]
DMA Заповнює:    |======= Половина передачі ========>| (Викликає HT ISR)
                |                                   |====== Повна передачі ============>| (Викликає TC ISR)
```

DMA контролер налаштовується на кільцевий трансфер (Circular Mode) із генеруванням двох апаратних переривань:
1. **Half-Transfer Interrupt (HT)**: Викликається, коли DMA заповнив першу половину масиву (Буфер A). У цей момент ЦПУ отримує сповіщення та обробляє Буфер A, поки DMA автономно заповнює Буфер B.
2. **Transfer Complete Interrupt (TC)**: Викликається, коли DMA заповнив другу половину масиву (Буфер B). ЦПУ обробляє Буфер B, поки DMA циклічно повертається на початок і заповнює Буфер A.

---

## 2. Математичний розрахунок часових обмежень

Для відсутності втрат даних час обробки одного буфера `T_proc` повинен бути суворо меншим за час його заповнення периферичним DMA `T_fill`:

```
T_fill = N / f_s
```

де `N` — розмір половини буфера (кількість відліків), а `f_s` — частота дискретизації АЦП (Гц).

Умова стабільності системи без втрат даних (Zero Buffer Overrun):

```
T_proc + T_latency_isr < T_fill
```

Розрахуємо тривалість заповнення буфера для частоти `f_s = 200000` Гц та розміру половини буфера `N = 512` відліків:

```
T_fill
= 512 / 200000           [ділення розміру буфера на частоту дискретизації]
= 0.00256 с = 2.56 мс    [тривалість автономного заповнення]
```

Обробка блоку з 512 відліків (наприклад, фільтрація) та вхід у переривання повинні сумарно займати менше 2.56 мс.

---

## 3. Програмна реалізація драйвера на C/C++

Нижче подано повний високопродуктивний модуль для мікроконтролерів ARM Cortex-M (STM32) / ESP32, який реалізує Ping-Pong DMA ADC буферизацію з нульовим копіюванням (Zero-Copy).

```cpp
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define ADC_PINGPONG_HALF_SIZE  512
#define ADC_PINGPONG_FULL_SIZE  (ADC_PINGPONG_HALF_SIZE * 2)

typedef enum {
    BUFFER_BLOCK_PING = 0,
    BUFFER_BLOCK_PONG = 1
} BufferBlock_t;

// Екземпляр драйвера Ping-Pong
typedef struct {
    uint16_t raw_dma_buffer[ADC_PINGPONG_FULL_SIZE];
    volatile bool ping_ready;
    volatile bool pong_ready;
    volatile uint32_t overrun_count;
    uint32_t samples_processed;
} AdcPingPongDriver_t;

static AdcPingPongDriver_t g_adc_driver;

/**
 * @brief Ініціалізація драйвера Ping-Pong
 */
void adc_pingpong_init(AdcPingPongDriver_t *drv) {
    memset((void*)drv, 0, sizeof(AdcPingPongDriver_t));
}

/**
 * @brief Переривання DMA: Половина передачі (Half Transfer - HT)
 * Викликається апаратно, коли заповнено Ping буфер.
 */
void adc_dma_half_transfer_isr(AdcPingPongDriver_t *drv) {
    if (drv->ping_ready) {
        // Переповнення: попередній Ping ще не оброблено ЦПУ!
        drv->overrun_count++;
    }
    drv->ping_ready = true;
}

/**
 * @brief Переривання DMA: Повна передача (Transfer Complete - TC)
 * Викликається апаратно, коли заповнено Pong буфер.
 */
void adc_dma_full_transfer_isr(AdcPingPongDriver_t *drv) {
    if (drv->pong_ready) {
        // Переповнення: попередній Pong ще не оброблено ЦПУ!
        drv->overrun_count++;
    }
    drv->pong_ready = true;
}

/**
 * @brief Алгоритм ДПФ/Обробки для одного блоку відліків (DSP Kernel)
 */
static void process_adc_block(const uint16_t *buffer, size_t size, BufferBlock_t block_type) {
    uint64_t sum = 0;
    uint16_t min_val = 0xFFFF;
    uint16_t max_val = 0;

    for (size_t i = 0; i < size; i++) {
        uint16_t val = buffer[i];
        sum += val;
        if (val < min_val) min_val = val;
        if (val > max_val) max_val = val;
    }

    float avg = (float)sum / (float)size;
    printf("[%s] Оброблено %5zu відліків | Середнє: %6.1f | Min: %4u | Max: %4u\n",
           (block_type == BUFFER_BLOCK_PING) ? "PING" : "PONG",
           size, avg, min_val, max_val);
}

/**
 * @brief Головна функція фонової обробки в main loop (без блокування переривань)
 */
void adc_pingpong_poll_process(AdcPingPongDriver_t *drv) {
    // Обробка Ping буфера
    if (drv->ping_ready) {
        const uint16_t *ping_ptr = &drv->raw_dma_buffer[0];
        process_adc_block(ping_ptr, ADC_PINGPONG_HALF_SIZE, BUFFER_BLOCK_PING);
        drv->ping_ready = false; // Скидання прапорця
        drv->samples_processed += ADC_PINGPONG_HALF_SIZE;
    }

    // Обробка Pong буфера
    if (drv->pong_ready) {
        const uint16_t *pong_ptr = &drv->raw_dma_buffer[ADC_PINGPONG_HALF_SIZE];
        process_adc_block(pong_ptr, ADC_PINGPONG_HALF_SIZE, BUFFER_BLOCK_PONG);
        drv->pong_ready = false; // Скидання прапорця
        drv->samples_processed += ADC_PINGPONG_HALF_SIZE;
    }
}

// Демонстраційний тест симуляції апаратного DMA
int main(void) {
    adc_pingpong_init(&g_adc_driver);
    printf("=== Демонстрація Подвійної Буферизації DMA ADC (Ping-Pong) ===\n");

    // Імітація кількох циклів роботи DMA
    for (int cycle = 0; cycle < 3; cycle++) {
        // Заповнення Ping буфера даними
        for (int i = 0; i < ADC_PINGPONG_HALF_SIZE; i++) {
            g_adc_driver.raw_dma_buffer[i] = (uint16_t)(2000 + (i % 100));
        }
        adc_dma_half_transfer_isr(&g_adc_driver);
        adc_pingpong_poll_process(&g_adc_driver);

        // Заповнення Pong буфера даними
        for (int i = 0; i < ADC_PINGPONG_HALF_SIZE; i++) {
            g_adc_driver.raw_dma_buffer[ADC_PINGPONG_HALF_SIZE + i] = (uint16_t)(1500 + (i % 200));
        }
        adc_dma_full_transfer_isr(&g_adc_driver);
        adc_pingpong_poll_process(&g_adc_driver);
    }

    printf("Разом оброблено відліків: %u | Кількість переповнень: %u\n",
           g_adc_driver.samples_processed, g_adc_driver.overrun_count);

    return 0;
}
```

---

## 4. Висновки

1. Подвійна буферизація за допомогою HT та TC переривань DMA повністю усуває стан гонки між периферією та ЦПУ.
2. Нульове копіювання (Zero-Copy) досягається передачею вказівок безпосередньо на halves робочого масиву DMA.
3. Обов'язково слід відстежувати прапорці переповнення `overrun_count` для діагностики випадків, коли обробка даних запізнюється відносно частоти АЦП.
