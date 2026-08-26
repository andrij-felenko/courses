# Неблокуючий кільцевий логер трафіку на базі DMA

Діагностика комунікаційних протоколів безпосередньо на мікроконтролері часто потрапляє в пастку: спроба вивести кожен прийнятий або надісланий байт через блокуючий `printf` чи синхронний `HAL_UART_Transmit` заморожує процесор на мілісекунди. За цей час апаратний приймач переповнюється (`Overrun Error`), таймери протоколу вичерпуються, а часова поведінка системи безповоротно спотворюється.

Щоб зафіксувати реальну послідовність обміну, мікроконтролер має знімати копію трафіку в нульовий час: апаратний контролер прямого доступу до пам'яті (DMA — Direct Memory Access) записує байти у виділений буфер в оперативній пам'яті (SRAM) без участі ядра процесора, а фоновий потік із низьким пріоритетом форматує зібрані кадри й відвантажує їх через окремий налагоджувальний порт або через спільну пам'ять налагоджувача (SEGGER RTT).

## Архітектура неблокуючого перехоплювача

Головне інженерне завдання системи логування трафіку — повністю розділити швидку фазу апаратного захоплення сирих даних у режимі реального часу від повільної фази їхнього форматування в текст та передачі на хост-комп'ютер.

Архітектура побудована навколо трьох взаємопов'язаних компонентів:
1. **Апаратний блок DMA з детекцією простою лінії (IDLE Line Interrupt)**: контролер DMA автоматично вичитує байти з регістру даних приймача `USART_RDR` і складає їх у циклічний буфер оперативної пам'яті. Коли передача чергового кадру завершується і на лінії встановлюється пасивний стан тривалістю в один байтовий інтервал, периферійний модуль генерує переривання простою `IDLE`, яке фіксує поточний розмір прийнятого кадру.
2. **Безблокуюча черга подій траси (Lock-Free SPSC Queue)**: кільцевий буфер типу Single-Producer Single-Consumer, що зв'язує швидкий обробник переривання (Producer) із фоновою задачею форматування (Consumer). Кожен запис містить мікросекундну мітку часу, напрямок передачі (`RX` чи `TX`), довжину пакета, лічильник пропущених пакетів та копію сирих байтів.
3. **Апаратний лічильник часу високої точності**: замість повільних системних викликів операційної системи реального часу (RTOS tick) використовується лічильник циклів ядра ARM Cortex-M `DWT->CYCCNT`, що забезпечує мікросекундну та наносекундну точність прив'язки подій.

## Розрахунок навантаження та синхронізація без блокувань

Спроба захистити чергу логів звичайним м'ютексом (Mutex) або вимкненням переривань (`__disable_irq()`) є грубою помилкою: якщо фонова задача форматування рядка утримує м'ютекс, обробник переривання UART не зможе зберегти новий вхідний пакет і вимушений буде чекати або втратити дані.

У кільцевій черзі типу Single-Producer Single-Consumer (SPSC) вказівник голови `head` модифікується виключно в контексті переривання, а вказівник хвоста `tail` — виключно в контексті фонової нитки. Обидва покажчики оголошуються як `volatile`, що запобігає їхньому кешуванню компілятором у регістрах загального призначення. Перевірка наявності вільного місця виконується однією атомарною операцією порівняння:

```
next_head = (head + 1) mod CAPACITY
якщо next_head == tail: черга переповнена (інкремент лічильника втрат)
інакше: запис даних, бар'єр пам'яті, оновлення head = next_head
```

Такий підхід гарантує, що час виконання операції додавання кадру в чергу всередині обробника переривання становить лише кілька десятків тактів процесора (менше 0.5 мікросекунди при тактовій частоті 168 МГц), що повністю виключає затримки та джитер у роботі основної програми.

## Реалізація на мовах C та C++

:::tabs
```c
/* trace_logger.h — Реалізація неблокуючого логера трафіку мовою C */
#ifndef TRACE_LOGGER_H
#define TRACE_LOGGER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define TRACE_PKT_MAX_LEN   128
#define TRACE_QUEUE_SLOTS    16

typedef enum {
    TRACE_DIR_RX = 0x01,
    TRACE_DIR_TX = 0x02
} trace_direction_t;

typedef struct {
    uint32_t timestamp_us;
    trace_direction_t direction;
    uint16_t length;
    uint8_t payload[TRACE_PKT_MAX_LEN];
} trace_record_t;

typedef struct {
    trace_record_t records[TRACE_QUEUE_SLOTS];
    volatile uint32_t head;
    volatile uint32_t tail;
    volatile uint32_t dropped_count;
} trace_queue_t;

void trace_queue_init(trace_queue_t *q);
bool trace_queue_push(trace_queue_t *q, trace_direction_t dir, uint32_t time_us,
                      const uint8_t *data, uint16_t len);
bool trace_queue_pop(trace_queue_t *q, trace_record_t *out_record);
size_t trace_format_hex(const trace_record_t *rec, char *out_buf, size_t max_out);

#endif /* TRACE_LOGGER_H */

/* trace_logger.c */
#include "trace_logger.h"
#include <string.h>
#include <stdio.h>

void trace_queue_init(trace_queue_t *q) {
    q->head = 0;
    q->tail = 0;
    q->dropped_count = 0;
}

bool trace_queue_push(trace_queue_t *q, trace_direction_t dir, uint32_t time_us,
                      const uint8_t *data, uint16_t len) {
    uint32_t next_head = (q->head + 1) % TRACE_QUEUE_SLOTS;
    if (next_head == q->tail) {
        q->dropped_count++;
        return false; /* Черга переповнена — фіксуємо втрату */
    }

    trace_record_t *slot = &q->records[q->head];
    slot->timestamp_us = time_us;
    slot->direction = dir;

    uint16_t copy_len = (len > TRACE_PKT_MAX_LEN) ? TRACE_PKT_MAX_LEN : len;
    slot->length = copy_len;
    memcpy(slot->payload, data, copy_len);

    q->head = next_head;
    return true;
}

bool trace_queue_pop(trace_queue_t *q, trace_record_t *out_record) {
    if (q->head == q->tail) {
        return false; /* Черга порожня */
    }

    *out_record = q->records[q->tail];
    q->tail = (q->tail + 1) % TRACE_QUEUE_SLOTS;
    return true;
}

size_t trace_format_hex(const trace_record_t *rec, char *out_buf, size_t max_out) {
    if (max_out < 64) return 0;

    uint32_t sec = rec->timestamp_us / 1000000;
    uint32_t us  = rec->timestamp_us % 1000000;
    const char *dir_str = (rec->direction == TRACE_DIR_RX) ? "RX" : "TX";

    int written = snprintf(out_buf, max_out, "[%04lu.%06lu] [%s] ",
                           (unsigned long)sec, (unsigned long)us, dir_str);
    if (written < 0 || (size_t)written >= max_out) return 0;

    size_t offset = (size_t)written;
    for (uint16_t i = 0; i < rec->length && (offset + 4) < max_out; i++) {
        written = snprintf(&out_buf[offset], max_out - offset, "%02X ", rec->payload[i]);
        if (written > 0) offset += (size_t)written;
    }

    if (offset < max_out) {
        out_buf[offset++] = '\n';
        out_buf[offset] = '\0';
    }
    return offset;
}
```
```cpp
// trace_logger.hpp — Реалізація неблокуючого логера трафіку мовою C++
#pragma once

#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <string_view>
#include <optional>
#include <algorithm>
#include <charconv>

enum class TraceDirection : uint8_t {
    Rx = 0x01,
    Tx = 0x02
};

struct TraceRecord {
    uint32_t timestamp_us{0};
    TraceDirection direction{TraceDirection::Rx};
    uint16_t length{0};
    std::array<uint8_t, 128> payload{};

    [[nodiscard]] std::span<const uint8_t> data() const noexcept {
        return std::span<const uint8_t>(payload.data(), length);
    }
};

template <size_t QueueCapacity = 16>
class TraceQueue {
public:
    constexpr TraceQueue() = default;

    bool push(TraceDirection dir, uint32_t time_us, std::span<const uint8_t> data) noexcept {
        const size_t next_head = (head_ + 1) % QueueCapacity;
        if (next_head == tail_) {
            ++dropped_count_;
            return false; // Буфер переповнено — фіксуємо втрату
        }

        auto& slot = records_[head_];
        slot.timestamp_us = time_us;
        slot.direction = dir;

        const size_t copy_len = std::min(data.size(), slot.payload.size());
        slot.length = static_cast<uint16_t>(copy_len);
        std::copy_n(data.data(), copy_len, slot.payload.begin());

        head_ = next_head;
        return true;
    }

    std::optional<TraceRecord> pop() noexcept {
        if (head_ == tail_) {
            return std::nullopt; // Порожньо
        }

        TraceRecord rec = records_[tail_];
        tail_ = (tail_ + 1) % QueueCapacity;
        return rec;
    }

    [[nodiscard]] size_t dropped() const noexcept { return dropped_count_; }
    [[nodiscard]] bool empty() const noexcept { return head_ == tail_; }

private:
    std::array<TraceRecord, QueueCapacity> records_{};
    volatile size_t head_{0};
    volatile size_t tail_{0};
    volatile size_t dropped_count_{0};
};

class TraceFormatter {
public:
    static size_t format_hex_dump(const TraceRecord& rec, std::span<char> out_buf) noexcept {
        if (out_buf.size() < 64) return 0;

        const uint32_t sec = rec.timestamp_us / 1'000'000;
        const uint32_t us  = rec.timestamp_us % 1'000'000;
        const std::string_view dir_str = (rec.direction == TraceDirection::Rx) ? "RX" : "TX";

        char* ptr = out_buf.data();
        char* const end = out_buf.data() + out_buf.size();

        // Запис заголовка часу та напрямку
        *ptr++ = '[';
        auto res = std::to_chars(ptr, end, sec);
        ptr = res.ptr;
        *ptr++ = '.';
        
        // Фіксовані 6 цифр мікросекунд
        char us_buf[8];
        auto us_res = std::to_chars(us_buf, us_buf + sizeof(us_buf), us);
        size_t us_len = us_res.ptr - us_buf;
        for (size_t i = 0; i < (6 - us_len) && ptr < end; ++i) *ptr++ = '0';
        for (size_t i = 0; i < us_len && ptr < end; ++i) *ptr++ = us_buf[i];

        *ptr++ = ']'; *ptr++ = ' '; *ptr++ = '[';
        for (char c : dir_str) if (ptr < end) *ptr++ = c;
        *ptr++ = ']'; *ptr++ = ' ';

        // Шістнадцятковий розбір байтів
        constexpr char hex_digits[] = "0123456789ABCDEF";
        for (uint8_t byte : rec.data()) {
            if (ptr + 3 >= end) break;
            *ptr++ = hex_digits[(byte >> 4) & 0x0F];
            *ptr++ = hex_digits[byte & 0x0F];
            *ptr++ = ' ';
        }

        if (ptr < end) *ptr++ = '\n';
        if (ptr < end) *ptr = '\0';

        return static_cast<size_t>(ptr - out_buf.data());
    }
};
```
:::

## Інтеграція з перериванням UART DMA та когерентність кешу

У коді ініціалізації мікроконтролера вмикається тактування блоку DWT для отримання точного мікросекундного часу без звернення до таймерів RTOS:

:::tabs
```c
/* Ініціалізація лічильника тактів ядра Cortex-M */
CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
```
```cpp
// Ініціалізація лічильника тактів ядра Cortex-M
CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
```
:::

Важливий аспект на високопродуктивних ядрах ARM Cortex-M7 (STM32H7, i.MX RT) — когерентність кешу даних (D-Cache). Контролер DMA записує байти безпосередньо в фізичну SRAM, оминаючи кеш ядра. Якщо процесор спробує прочитати буфер без інвалідації кеш-ліній, він зчитає застарілі дані:

:::tabs
```c
/* Для ядер Cortex-M7 з увімкненим D-Cache */
SCB_InvalidateDCache_by_Addr((uint32_t*)g_rx_dma_buf, sizeof(g_rx_dma_buf));
```
```cpp
// Для ядер Cortex-M7 з увімкненим D-Cache
SCB_InvalidateDCache_by_Addr(reinterpret_cast<uint32_t*>(g_dma_buffer.data()), g_dma_buffer.size());
```
:::

Обробник переривання UART фіксує момент закінчення кадру за прапорцем простою лінії та зберігає дані в чергу:

:::tabs
```c
/* Обробник переривання DMA Idle Line у stm32f4xx_it.c */
extern UART_HandleTypeDef huart2;
extern trace_queue_t g_trace_queue;
extern uint8_t g_rx_dma_buf[256];

void USART2_IRQHandler(void) {
    if (__HAL_UART_GET_FLAG(&huart2, UART_FLAG_IDLE) != RESET) {
        __HAL_UART_CLEAR_IDLEFLAG(&huart2);

        /* Визначаємо, скільки байтів записав контролер DMA */
        uint16_t remaining = __HAL_DMA_GET_COUNTER(huart2.hdmarx);
        uint16_t received_bytes = sizeof(g_rx_dma_buf) - remaining;

        if (received_bytes > 0) {
            /* Отримуємо мікросекунди без плаваючої коми */
            uint32_t now_us = DWT->CYCCNT / (SystemCoreClock / 1000000);
            trace_queue_push(&g_trace_queue, TRACE_DIR_RX, now_us, g_rx_dma_buf, received_bytes);
        }

        /* Перезапуск DMA на наступний прийом */
        HAL_UART_AbortReceive(&huart2);
        HAL_UART_Receive_DMA(&huart2, g_rx_dma_buf, sizeof(g_rx_dma_buf));
    }
    HAL_UART_IRQHandler(&huart2);
}
```
```cpp
// Обробник переривання у стилі C++
extern "C" void USART2_IRQHandler(void);

namespace {
    TraceQueue<32> g_app_trace_queue;
    std::array<uint8_t, 256> g_dma_buffer{};
}

void on_uart_idle_detected(size_t bytes_transferred, uint32_t clock_cycles, uint32_t cpu_hz) noexcept {
    if (bytes_transferred == 0) return;

    const uint32_t now_us = clock_cycles / (cpu_hz / 1'000'000);
    g_app_trace_queue.push(TraceDirection::Rx, now_us,
                           std::span<const uint8_t>(g_dma_buffer.data(), bytes_transferred));
}
```
:::

## Налаштування каналу відвантаження через SEGGER RTT

Якщо для виведення траси використовується інтерфейс SEGGER Real Time Transfer (RTT), буфер виводу налаштовується в неблокуючому режимі пропуску записів у разі переповнення (`SEGGER_RTT_MODE_NO_BLOCK_SKIP`):

:::tabs
```c
/* Налаштування неблокуючого налагоджувального каналу RTT Channel 1 */
SEGGER_RTT_ConfigUpBuffer(1, "CommTrace", g_rtt_trace_buf, sizeof(g_rtt_trace_buf),
                          SEGGER_RTT_MODE_NO_BLOCK_SKIP);
```
```cpp
// Налаштування неблокуючого налагоджувального каналу RTT Channel 1
SEGGER_RTT_ConfigUpBuffer(1, "CommTrace", g_rtt_trace_buf.data(), g_rtt_trace_buf.size(),
                          SEGGER_RTT_MODE_NO_BLOCK_SKIP);
```
:::

У такому режимі запис у пам'ять виконується парою асемблерних інструкцій. Якщо хост-комп'ютер тимчасово відключено або утиліта RTT Viewer не запущена, мікроконтролер не блокується в очікуванні зчитування, а продовжує виконання програми в штатному темпі.

## Експорт траси та перетворення у PCAP через text2pcap

Фонова задача вичитує події з черги `trace_queue_pop` і відправляє сформовані текстові рядки через окремий налагоджувальний порт або у виділений буфер SEGGER RTT.

Згенерований дамп має стандартизований вигляд:
```
[0001.045230] [RX] AA 55 01 00 02 0A 00 E8 03 80 0C B8 0B F4 01 04 00 3C 9A
[0001.050110] [TX] AA 55 02 00 04 03 00 01 00 00 E1 5F
```

Для імпорту цього тексту у Wireshark використовується утиліта `text2pcap`, що входить до складу дистрибутиву аналізатора:

```bash
# Перетворення Hex-дампу на PCAPNG із прив'язкою до UDP-порту 8888
text2pcap -t "%H:%M:%S." -u 8888,8888 -D uart_trace.hex uart_trace.pcapng
```

Параметр `-t "%H:%M:%S."` задає шаблон розпізнавання міток часу, `-u 8888,8888` створює синтетичний заголовок UDP із зазначеними портами відправника й отримувача, а опція `-D` активує режим детекції напрямку (`RX` чи `TX`), що відображається у Wireshark у вигляді правильного чергування запитів і відповідей.

Отриманий файл `uart_trace.pcapng` відкривається у Wireshark, де розбирається створеним Lua-дисектором так само зручно, як і трафік Ethernet, дозволяючи бачити повну хронологію обміну з мікросекундними затримками між запитами й відповідями.
