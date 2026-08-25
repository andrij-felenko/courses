# ⚙️ Діагностика, захист та трасування купи у FreeRTOS та ESP-IDF

Динамічна пам'ять у вбудованій системі рідко відмовляє миттєво: найчастіше вона деградує приховано. Задача виділяє буфер для чергового кадру, але через помилку в розрахунку зсуву пише на два байти далі виділеної межі, пошкоджуючи заголовок сусіднього вільного блока. Система продовжує працювати ще кілька хвилин, поки інша задача не спробує розірвати або об'єднати цей пошкоджений блок — і в цей момент виникає апаратне виключення `HardFault`, адреса якого не має нічого спільного з місцем первинної помилки.

Щоб виявляти такі помилки до переходу пристрою в аварійний стан, FreeRTOS та ESP-IDF надають механізми діагностики трьох рівнів: поточні лічильники мінімального залишку (водяні знаки), захисне отруєння буферів (heap poisoning) та покрокове трасування викликів алокатора.

---

### Відстеження ватерлінії пам'яті (High Water Mark)

Функція `xPortGetFreeHeapSize()` повертає сумарну кількість вільних байтів у купі на момент виклику. Проте ця цифра оманлива: вона нічого не каже про те, чи не опускався рівень пам'яті до критичного нуля секунду тому, коли система обробляла сплеск мережевих пакетів.

Для контролю критичного мінімуму FreeRTOS веде внутрішню змінну `xMinimumEverFreeBytesRemaining`, значення якої оновлюється під час кожного виділення `pvPortMalloc()`. Прочитати її можна через функцію `xPortGetMinimumEverFreeHeapSize()`.

:::tabs
```c
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char *TAG = "HEAP_MON";

void heap_monitor_task(void *pvParameters)
{
    (void)pvParameters;

    while (1) {
        size_t free_bytes = xPortGetFreeHeapSize();
        size_t min_ever_free = xPortGetMinimumEverFreeHeapSize();

        ESP_LOGI(TAG, "Поточна вільна RAM: %u Б, історичний мінімум: %u Б",
                 (unsigned int)free_bytes,
                 (unsigned int)min_ever_free);

        /* Якщо історичний мінімум наблизився до небезпечної межі */
        if (min_ever_free < 4096) {
            ESP_LOGW(TAG, "УВАГА: Небезпечне вичерпання купи! Запас < 4 КБ");
        }

        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}
```
```cpp
#include <span>
#include <chrono>
#include <concepts>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

class HeapMonitor {
public:
    explicit constexpr HeapMonitor(size_t warning_threshold_bytes = 4096) noexcept
        : threshold_bytes_{warning_threshold_bytes} {}

    void inspect_and_log() const noexcept {
        const size_t free_bytes = xPortGetFreeHeapSize();
        const size_t min_ever_free = xPortGetMinimumEverFreeHeapSize();

        ESP_LOGI("HEAP_MON", "Поточна RAM: %zu Б, історичний мінімум: %zu Б",
                 free_bytes, min_ever_free);

        if (min_ever_free < threshold_bytes_) {
            ESP_LOGW("HEAP_MON", "Критичний запас пам'яті: %zu Б (поріг %zu Б)",
                     min_ever_free, threshold_bytes_);
        }
    }

private:
    size_t threshold_bytes_;
};

extern "C" void heap_monitor_task_cpp(void *pvParameters)
{
    (void)pvParameters;
    const HeapMonitor monitor{4096};

    while (true) {
        monitor.inspect_and_log();
        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}
```
:::

---

### Обробник вичерпання пам'яті: vApplicationMallocFailedHook

Якщо `pvPortMalloc()` або `heap_caps_malloc()` не можуть знайти суцільний блок потрібного розміру, вони повертають `NULL`. Якщо у конфігурації `FreeRTOSConfig.h` увімкнено параметр `configUSE_MALLOC_FAILED_HOOK = 1`, ядро перед поверненням `NULL` автоматично викликає функцію зворотного виклику `vApplicationMallocFailedHook()`.

Це дає змогу зафіксувати аварійний стан у журналі, зберегти діагностичний зліпок у пам'ять RTC або передати сигнал тривоги до перезавантаження процесора.

:::tabs
```c
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_system.h"

void vApplicationMallocFailedHook(void)
{
    TaskHandle_t failed_task = xTaskGetCurrentTaskHandle();
    const char *task_name = pcTaskGetName(failed_task);

    ESP_LOGE("CRITICAL", "КРИТИЧНА ПОМИЛКА: pvPortMalloc() повернув NULL у задачі '%s'!",
             task_name ? task_name : "UNKNOWN");
    ESP_LOGE("CRITICAL", "Вільна пам'ять на момент збою: %u Б",
             (unsigned int)xPortGetFreeHeapSize());

    /* У бойовій системі: фіксація в NVS/RTC та контрольоване перезавантаження */
    esp_restart();
}
```
```cpp
#include <string_view>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_system.h"

namespace diagnostics {

[[noreturn]] void handle_malloc_failure() noexcept
{
    const TaskHandle_t task = xTaskGetCurrentTaskHandle();
    const char * const raw_name = pcTaskGetName(task);
    const std::string_view task_name = (raw_name != nullptr) ? raw_name : "UNKNOWN";

    ESP_LOGE("CRITICAL", "Аварія алокації у задачі: %.*s",
             static_cast<int>(task_name.size()), task_name.data());
    ESP_LOGE("CRITICAL", "Залишок купи: %zu Б", xPortGetFreeHeapSize());

    esp_restart();
}

} // namespace diagnostics

extern "C" void vApplicationMallocFailedHook(void)
{
    diagnostics::handle_malloc_failure();
}
```
:::

---

### Захисне отруєння пам'яті (Heap Poisoning) та перевірка канарейок

Пошкодження пам'яті найчастіше виникає у двох формах:
1. **Переповнення буфера (Buffer Overflow):** запис даних за межі виділеного блока з перетиранням заголовка наступного блока.
2. **Використання після звільнення (Use-After-Free):** читання або запис у блок після виклику `free()`, коли пам'ять уже передано іншій підсистемі.

В ESP-IDF вбудовано дворівневу систему апаратного та програмного отруєння пам'яті через конфігурацію Kconfig:

```text
CONFIG_HEAP_POISONING_COMPREHENSIVE=y
CONFIG_HEAP_TRACING=y
```

При базовому отруєнні (`CONFIG_HEAP_POISONING_LIGHT`) алокатор додає 4-байтні або 8-байтні сигнатурні слова-канарейки (canaries) безпосередньо перед корисним навантаженням користувача та одразу після нього. Значення канарейок заповнюються фіксованими магічними константами (наприклад, `0xBAADF00D` для голови та `0xF00DBAAD` для хвоста).

При повному отруєнні (`CONFIG_HEAP_POISONING_COMPREHENSIVE`):
- Уся нерозподілена пам'ять при ініціалізації заповнюється шаблоном `0xa5a5a5a5`.
- Звільнені блоки при виклику `free()` негайно перезаписуються байтами `0xcececece`.
- Якщо програма спробує прочитати звільнений блок, покажчики всередині нього міститимуть некоректну адресу `0xcececece`, звернення за якою спричиняє негайний апаратний збій читання `LoadProhibited` або `HardFault`, локалізуючи помилку в точці несанкціонованого доступу.

Функція `heap_caps_check_integrity_all()` перевіряє цілісність усіх заголовків та канарейок у кожному зареєстрованому пулі пам'яті.

:::tabs
```c
#include "esp_heap_caps.h"
#include "esp_log.h"

void check_heap_corruption_example(void)
{
    /* Ручна перевірка цілісності всіх зв'язних списків купи */
    bool is_healthy = heap_caps_check_integrity_all(true);

    if (is_healthy) {
        ESP_LOGI("HEAP_CHECK", "Цілісність усіх банків пам'яті підтверджено");
    } else {
        ESP_LOGE("HEAP_CHECK", "ВИЯВЛЕНО ПОШКОДЖЕННЯ КУПИ! Зруйновано канарейки або заголовки");
    }
}
```
```cpp
#include "esp_heap_caps.h"
#include "esp_log.h"

struct HeapIntegrity {
    [[nodiscard]] static bool verify_all_regions(bool print_errors = true) noexcept {
        return heap_caps_check_integrity_all(print_errors);
    }
};

void run_diagnostics_cpp()
{
    if (HeapIntegrity::verify_all_regions()) {
        ESP_LOGI("HEAP_CHECK", "Купа неушкоджена.");
    } else {
        ESP_LOGE("HEAP_CHECK", "Аварія структури купи!");
    }
}
```
:::

---

### Трасування витоків пам'яті через Heap Tracing

Коли пристрій втрачає пам'ять поступово (по кілька байтів на хвилину), знайти винуватця прямим оглядом коду складно. Модуль `esp_heap_trace` в ESP-IDF перехоплює всі операції виділення та звільнення, записуючи адреси викликів (program counter) у кільцевий буфер.

Трасувальник підтримує два режими:
1. `HEAP_TRACE_ALL` — записує всі виклики `malloc` та `free` підряд (використовується для профілювання часових діаграм пам'яті).
2. `HEAP_TRACE_LEAKS` — видаляє із буфера пари викликів, які були успішно вивільнені, залишаючи лише ті блоки, що залишилися «висіти» у пам'яті на момент зупинки трасування.

:::tabs
```c
#include "esp_heap_trace.h"
#include "esp_log.h"

#define NUM_RECORDS 100
static heap_trace_record_t trace_records[NUM_RECORDS];

void detect_memory_leaks(void (*routine_to_test)(void))
{
    /* 1. Ініціалізація трасувальника */
    ESP_ERROR_CHECK(heap_trace_init_standalone(trace_records, NUM_RECORDS));

    /* 2. Запуск запису тільки блоків, які не були звільнені */
    ESP_ERROR_CHECK(heap_trace_start(HEAP_TRACE_LEAKS));

    /* 3. Виконання досліджуваного сценарію */
    routine_to_test();

    /* 4. Зупинка трасування */
    ESP_ERROR_CHECK(heap_trace_stop());

    /* 5. Друк знайдених витоків */
    ESP_LOGI("TRACE", "Результати аналізу витоків:");
    heap_trace_dump();
}
```
```cpp
#include <array>
#include <concepts>
#include "esp_heap_trace.h"
#include "esp_log.h"

template <size_t RecordCount = 128>
class ScopedHeapLeakTracer {
public:
    ScopedHeapLeakTracer() {
        ESP_ERROR_CHECK(heap_trace_init_standalone(records_.data(), records_.size()));
        ESP_ERROR_CHECK(heap_trace_start(HEAP_TRACE_LEAKS));
    }

    ~ScopedHeapLeakTracer() noexcept {
        heap_trace_stop();
        ESP_LOGI("LEAK_TRACE", "Аналіз невивільнених алокацій у блоці:");
        heap_trace_dump();
    }

    ScopedHeapLeakTracer(const ScopedHeapLeakTracer &) = delete;
    ScopedHeapLeakTracer &operator=(const ScopedHeapLeakTracer &) = delete;

private:
    std::array<heap_trace_record_t, RecordCount> records_{};
};

void profile_subsystem_cpp(void (*workload)())
{
    {
        ScopedHeapLeakTracer<64> tracer;
        workload();
    } // ~ScopedHeapLeakTracer автоматично зупинить трасування та роздрукує звіт
}
```
:::

Вивід `heap_trace_dump()` містить точні адреси інструкцій процесора, які викликали виділення втрачених блоків. За допомогою утиліти `addr2line` із тулчейну компілятора (наприклад, `xtensa-esp32-elf-addr2line` або `riscv32-esp-elf-addr2line`) шістнадцяткові адреси транслюються безпосередньо у номери рядків вихідних файлів проєкту:

```bash
xtensa-esp32-elf-addr2line -e build/my_firmware.elf 0x400d284a 0x400d31bc
# Вивід:
# /project/main/network.c:142
# /project/main/parser.c:87
```

---

### Обробка помилок нестачі пам'яті через Callback в ESP-IDF

Окрім класичного FreeRTOS хука `vApplicationMallocFailedHook()`, фреймворк ESP-IDF надає механізм реєстрації користувацького зворотного виклику через функцію `heap_caps_register_failed_alloc_callback()`. Це дає змогу отримувати точні параметри відхиленого запиту: розмір та запитані прапорці можливостей.

:::tabs
```c
#include "esp_heap_caps.h"
#include "esp_log.h"

static void on_allocation_failure(size_t size, uint32_t caps, const char *function_name)
{
    ESP_LOGE("HEAP_FAIL", "Відхилено запит на %u байтів у функції %s (можливості: 0x%08x)",
             (unsigned int)size,
             function_name ? function_name : "UNKNOWN",
             (unsigned int)caps);

    if (caps & MALLOC_CAP_DMA) {
        ESP_LOGE("HEAP_FAIL", "Критичний збій: вичерпано внутрішню пам'ять DMA!");
    } else if (caps & MALLOC_CAP_SPIRAM) {
        ESP_LOGE("HEAP_FAIL", "Вичерпано зовнішню пам'ять PSRAM!");
    }
}

void register_heap_fail_handler(void)
{
    esp_err_t err = heap_caps_register_failed_alloc_callback(on_allocation_failure);
    if (err == ESP_OK) {
        ESP_LOGI("HEAP_FAIL", "Обробник збоїв алокації успішно зареєстровано");
    }
}
```
```cpp
#include "esp_heap_caps.h"
#include "esp_log.h"
#include <string_view>

namespace memory_protection {

class AllocationFailureHandler {
public:
    static void init() noexcept {
        heap_caps_register_failed_alloc_callback(&callback_bridge);
    }

private:
    static void callback_bridge(size_t size, uint32_t caps, const char *function_name) noexcept {
        const std::string_view fn = (function_name != nullptr) ? function_name : "anonymous";
        ESP_LOGE("CPP_HEAP", "Неможливо виділити %zu Б у %.*s (caps: 0x%08x)",
                 size, static_cast<int>(fn.size()), fn.data(), caps);
    }
};

} // namespace memory_protection

void init_diagnostics_cpp()
{
    memory_protection::AllocationFailureHandler::init();
}
```
:::

---

### Чому не можна викликати malloc з обробника переривань (ISR)

Класична пастка для розробників мікроконтролерів — спроба виділити пам'ять під сирий буфер безпосередньо всередині обробника переривання (ISR, Interrupt Service Routine).

У FreeRTOS принципово не існує функції `pvPortMallocFromISR()`. Причина полягає в архітектурі критичних секцій алокатора:
1. Для захисту списків вільних блоків `heap_4` зупиняє планувальник (`vTaskSuspendAll()`) або входить у критичну секцію `taskENTER_CRITICAL()`.
2. Виклик блокувальних примітивів або функцій зупинки планувальника всередині ISR апаратно заборонений і призводить до HardFault або порушення логіки ядра.
3. Пошук вільного блока в списку First-Fit має змінну тривалість `O(N)`. Виконання неконстантного алгоритму всередині ISR блокує всі інші переривання системи, викликаючи деградацію радіотрактів та пропуск подій таймерів.

Якщо апаратне переривання приймає дані змінного розміру, правильний інженерний патерн полягає у використанні заздалегідь виділених статичних кільцевих буферів або передачі сповіщення у фонову задачу через чергу `xQueueSendFromISR()`, де задача вже виконує повноцінне виділення пам'яті в контексті потоку.

:::tabs
```c
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"

typedef struct {
    uint32_t length;
    uint8_t  payload[64]; /* Статичний фіксований буфер під переривання */
} isr_packet_t;

static QueueHandle_t isr_packet_queue = NULL;

/* Обробник апаратного переривання: жодних викликів malloc! */
void IRAM_ATTR uart_rx_isr_handler(void)
{
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    isr_packet_t packet;

    packet.length = 32; /* Зчитування з регістру FIFO */
    /* ... заповнення packet.payload ... */

    /* Передаємо фіксовану структуру через чергу без динамічної алокації */
    xQueueSendFromISR(isr_packet_queue, &packet, &xHigherPriorityTaskWoken);

    if (xHigherPriorityTaskWoken == pdTRUE) {
        portYIELD_FROM_ISR();
    }
}
```
```cpp
#include <array>
#include <cstdint>
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"

struct IsrFixedPacket {
    std::uint32_t length{0};
    std::array<std::uint8_t, 64> payload{};
};

class IsrBufferBridge {
public:
    explicit IsrBufferBridge(QueueHandle_t target_queue) noexcept
        : queue_{target_queue} {}

    void IRAM_ATTR handle_incoming_bytes_isr(const std::span<const uint8_t> rx_data) noexcept {
        BaseType_t higher_prio_woken = pdFALSE;
        IsrFixedPacket pkt{};
        pkt.length = static_cast<std::uint32_t>(rx_data.size());

        for (std::size_t i = 0; i < rx_data.size() && i < pkt.payload.size(); ++i) {
            pkt.payload[i] = rx_data[i];
        }

        xQueueSendFromISR(queue_, &pkt, &higher_prio_woken);

        if (higher_prio_woken == pdTRUE) {
            portYIELD_FROM_ISR();
        }
    }

private:
    QueueHandle_t queue_{nullptr};
};
```
:::

Використання цих діагностичних інструментів та архітектурних патернів дає змогу виявити помилки розрахунку пам'яті на етапі розробки та стендового тестування, гарантуючи передбачувану роботу мікроконтролера в польових умовах.
