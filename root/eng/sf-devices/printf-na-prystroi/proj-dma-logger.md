# ⚙️ Асинхронний логер UART DMA з кільцевим буфером

Виклик функції друку всередині переривання таймера чи високочастотного контуру стабілізації не повинен зупиняти обчислення на мілісекунди в очікуванні готовності передавача UART. Якщо ядро процесора витрачає час на побайтове опитування регістрів передавача, система втрачає здатність вчасно реагувати на зовнішні події та зриває жорсткі часові обмеження. Асинхронна архітектура логування розв'язує цю проблему через поділ процесу на два незалежні етапи: швидкий запис відформатованого рядка в оперативну пам'ять (кільцевий буфер FIFO) та фонову вичитку цих даних апаратним контролером прямого доступу до пам'яті (DMA).

## Архітектура неблокуючого буфера та запуск DMA

Контролер DMA потребує неперервного (лінійного) діапазону адрес у пам'яті для виконання транзакції. У кільцевому буфері дані часто записуються з переходом через фізичний кінець масиву (wrap-around). Тому драйвер асинхронного виводу розбиває передачу на лінійні відрізки.

```
       [Початок буфера]                      [Кінець буфера]
Параметри: |---------|===================|---------|
                     ↑                   ↑
                 rd_tail              wr_head
               (читає DMA)          (пише ядро)
               
Випадок 1: wr_head >= rd_tail → лінійний блок розміром (wr_head - rd_tail)
Випадок 2: wr_head <  rd_tail → перший блок від rd_tail до кінця буфера,
                                другий блок від 0 до wr_head після переривання
```

Коли застосунок додає повідомлення в буфер:
1. Байти копіюються в позицію `wr_head`, а сам покажчик просувається вперед з урахуванням маски розміру буфера (розмір обирається степенем двійки, щоб замінити операцію взяття залишку `%` на швидку бітову операцію `&`).
2. Якщо на момент запису DMA не зайнятий передачею попередньої порції даних, драйвер обчислює довжину неперервного відрізка від `rd_tail` до кінця буфера (або до `wr_head`, якщо переходу через край ще не відбулося) і конфігурує канали DMA на передачу цього сегмента.
3. Коли контролер DMA завершує передачу встановленого блоку, генерується апаратне переривання Transfer Complete (TC). Обробник переривання зміщує `rd_tail` на кількість реально відправлених байтів. Якщо в буфері лишилися нові дані, обробник негайно перезапускає DMA для наступного сегмента.

## Режими роботи DMA: прямий та FIFO

Апаратні контролери DMA (наприклад, у мікроконтролерах STM32 сімейств F4/F7/H7) підтримують два режими взаємодії з шиною:
- **Direct Mode (прямий режим):** кожен запит від передавача UART негайно ініціює одиночне читання з оперативної пам'яті по системній шині AHB/AXI. Цей режим має мінімальну затримку реакції, але збільшує конкуренцію за доступ до пам'яті з процесорним ядром.
- **FIFO Mode з пакетною передачею (Burst Transfer):** контролер DMA попередньо зчитує з пам'яті пакет із 4, 8 або 16 байтів у свій внутрішній апаратний FIFO-буфер за одну транзакцію шини, після чого побайтово віддає їх передавачу UART без додаткових звернень до RAM. Це значно розвантажує арбітр шини пам'яті.

## Життєвий цикл переривань та керування станом

Драйвер DMA опрацьовує три ключові апаратні прапорці:
- **Transfer Complete (TC):** контролер переслав усі замовлені байти в буфер передавача UART. Обробник переривання звільняє переданий діапазон у кільцевому буфері та запускає наступний лінійний відрізок, якщо `head != tail`.
- **Half Transfer (HT):** використовується в режимах подвійної буферизації або для відстеження високого рівня заповнення (high-watermark) буфера.
- **Transfer Error (TE):** виникає при спробі доступу DMA до забороненої ділянки шини (наприклад, неіснуючої пам'яті або при порушенні прав доступу MPU). Обробник мусить скинути статус помилки та аварійно перезапустити канал.

## Реалізація модуля логування

Нижче наведено повну реалізацію асинхронного логера. Реалізація забезпечує атомарність оновлення покажчиків, захист критичних секцій від гонок між перериваннями та підрахунок відкинутих байтів у разі вичерпання вільного місця в буфері.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
#include <stdarg.h>
#include <stdio.h>

#define UART_LOG_BUFFER_SIZE 2048U
#define UART_LOG_BUFFER_MASK (UART_LOG_BUFFER_SIZE - 1U)

typedef struct {
    uint8_t buffer[UART_LOG_BUFFER_SIZE];
    volatile size_t head;            /* Позиція запису ядром */
    volatile size_t tail;            /* Позиція читання DMA */
    volatile size_t dma_active_len;  /* Кількість байтів у поточній транзакції DMA */
    volatile bool dma_busy;          /* Прапорець активної передачі */
    volatile uint32_t dropped_bytes; /* Лічильник втрачених байтів при переповненні */
} async_logger_t;

static async_logger_t g_logger;

/* Апаратні функції запуску та синхронізації (адаптуються під конкретний MCU) */
extern void hw_uart_dma_start_transfer(const uint8_t *src, size_t length);
extern void hw_enter_critical(void);
extern void hw_exit_critical(void);
extern void hw_dcache_clean_range(const void *addr, size_t size);

void async_logger_init(void) {
    g_logger.head = 0;
    g_logger.tail = 0;
    g_logger.dma_active_len = 0;
    g_logger.dma_busy = false;
    g_logger.dropped_bytes = 0;
}

static size_t async_logger_available_space(void) {
    size_t head = g_logger.head;
    size_t tail = g_logger.tail;
    if (head >= tail) {
        return (UART_LOG_BUFFER_SIZE - 1U) - (head - tail);
    }
    return (tail - head) - 1U;
}

static void async_logger_kick_dma_locked(void) {
    if (g_logger.dma_busy) {
        return;
    }
    if (g_logger.head == g_logger.tail) {
        return; /* Буфер порожній */
    }

    size_t chunk_len;
    if (g_logger.head > g_logger.tail) {
        chunk_len = g_logger.head - g_logger.tail;
    } else {
        /* Передача до фізичного кінця масиву */
        chunk_len = UART_LOG_BUFFER_SIZE - g_logger.tail;
    }

    g_logger.dma_busy = true;
    g_logger.dma_active_len = chunk_len;

    /* Скидання кешу даних перед стартом читання контролером DMA */
    hw_dcache_clean_range(&g_logger.buffer[g_logger.tail], chunk_len);
    hw_uart_dma_start_transfer(&g_logger.buffer[g_logger.tail], chunk_len);
}

size_t async_logger_write(const uint8_t *data, size_t len) {
    if (data == NULL || len == 0) {
        return 0;
    }

    hw_enter_critical();

    size_t free_space = async_logger_available_space();
    if (len > free_space) {
        /* При переповненні відкидаємо надлишок і фіксуємо втрату */
        g_logger.dropped_bytes += (uint32_t)(len - free_space);
        len = free_space;
    }

    if (len == 0) {
        hw_exit_critical();
        return 0;
    }

    size_t current_head = g_logger.head;
    size_t first_part = UART_LOG_BUFFER_SIZE - current_head;

    if (len <= first_part) {
        memcpy(&g_logger.buffer[current_head], data, len);
        g_logger.head = (current_head + len) & UART_LOG_BUFFER_MASK;
    } else {
        memcpy(&g_logger.buffer[current_head], data, first_part);
        memcpy(&g_logger.buffer[0], data + first_part, len - first_part);
        g_logger.head = (len - first_part) & UART_LOG_BUFFER_MASK;
    }

    async_logger_kick_dma_locked();

    hw_exit_critical();
    return len;
}

int async_logger_printf(const char *fmt, ...) {
    char temp_staging[128];
    va_list args;
    va_start(args, fmt);
    int len = vsnprintf(temp_staging, sizeof(temp_staging), fmt, args);
    va_end(args);

    if (len > 0) {
        size_t to_write = ((size_t)len < sizeof(temp_staging)) ? (size_t)len : (sizeof(temp_staging) - 1U);
        async_logger_write((const uint8_t*)temp_staging, to_write);
    }
    return len;
}

/* Обробник переривання DMA Transfer Complete (ISR) */
void async_logger_dma_isr_handler(void) {
    /* Оновлюємо хвіст буфера на довжину відправленої пачки */
    g_logger.tail = (g_logger.tail + g_logger.dma_active_len) & UART_LOG_BUFFER_MASK;
    g_logger.dma_active_len = 0;
    g_logger.dma_busy = false;

    /* Запускаємо наступний фрагмент, якщо в буфері лишилися дані */
    async_logger_kick_dma_locked();
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <string_view>
#include <span>
#include <array>
#include <atomic>
#include <cstdio>
#include <cstdarg>

extern "C" void hw_uart_dma_start_transfer(const uint8_t *src, size_t length);
extern "C" void hw_enter_critical(void);
extern "C" void hw_exit_critical(void);
extern "C" void hw_dcache_clean_range(const void *addr, size_t size);

template <size_t BufferSize = 2048>
class DmaAsyncLogger {
    static_assert((BufferSize & (BufferSize - 1)) == 0, "Розмір буфера мусить бути степенем двійки!");
    static constexpr size_t BufferMask = BufferSize - 1;

public:
    constexpr DmaAsyncLogger() = default;

    void init() noexcept {
        head_.store(0, std::memory_order_relaxed);
        tail_.store(0, std::memory_order_relaxed);
        dma_active_len_ = 0;
        dma_busy_.store(false, std::memory_order_relaxed);
        dropped_bytes_.store(0, std::memory_order_relaxed);
    }

    size_t write(std::string_view message) noexcept {
        return write(std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(message.data()), message.size()));
    }

    size_t write(std::span<const uint8_t> data) noexcept {
        if (data.empty()) {
            return 0;
        }

        CriticalSectionGuard lock;

        const size_t free_space = available_space();
        size_t bytes_to_write = data.size();

        if (bytes_to_write > free_space) {
            dropped_bytes_.fetch_add(bytes_to_write - free_space, std::memory_order_relaxed);
            bytes_to_write = free_space;
        }

        if (bytes_to_write == 0) {
            return 0;
        }

        const size_t cur_head = head_.load(std::memory_order_relaxed);
        const size_t first_part = BufferSize - cur_head;

        if (bytes_to_write <= first_part) {
            std::memcpy(&storage_[cur_head], data.data(), bytes_to_write);
            head_.store((cur_head + bytes_to_write) & BufferMask, std::memory_order_release);
        } else {
            std::memcpy(&storage_[cur_head], data.data(), first_part);
            std::memcpy(&storage_[0], data.data() + first_part, bytes_to_write - first_part);
            head_.store((bytes_to_write - first_part) & BufferMask, std::memory_order_release);
        }

        kick_dma_locked();
        return bytes_to_write;
    }

    int print_fmt(const char* fmt, ...) noexcept {
        std::array<char, 128> staging{};
        va_list args;
        va_start(args, fmt);
        const int len = vsnprintf(staging.data(), staging.size(), fmt, args);
        va_end(args);

        if (len > 0) {
            const size_t count = (static_cast<size_t>(len) < staging.size()) ? static_cast<size_t>(len) : (staging.size() - 1);
            write(std::string_view(staging.data(), count));
        }
        return len;
    }

    void on_dma_transfer_complete_isr() noexcept {
        const size_t cur_tail = tail_.load(std::memory_order_relaxed);
        tail_.store((cur_tail + dma_active_len_) & BufferMask, std::memory_order_release);
        dma_active_len_ = 0;
        dma_busy_.store(false, std::memory_order_relaxed);

        kick_dma_locked();
    }

    [[nodiscard]] uint32_t dropped_count() const noexcept {
        return dropped_bytes_.load(std::memory_order_relaxed);
    }

private:
    struct CriticalSectionGuard {
        CriticalSectionGuard() noexcept { hw_enter_critical(); }
        ~CriticalSectionGuard() noexcept { hw_exit_critical(); }
        CriticalSectionGuard(const CriticalSectionGuard&) = delete;
        CriticalSectionGuard& operator=(const CriticalSectionGuard&) = delete;
    };

    [[nodiscard]] size_t available_space() const noexcept {
        const size_t h = head_.load(std::memory_order_relaxed);
        const size_t t = tail_.load(std::memory_order_relaxed);
        if (h >= t) {
            return (BufferSize - 1) - (h - t);
        }
        return (t - h) - 1;
    }

    void kick_dma_locked() noexcept {
        if (dma_busy_.load(std::memory_order_relaxed)) {
            return;
        }

        const size_t h = head_.load(std::memory_order_relaxed);
        const size_t t = tail_.load(std::memory_order_relaxed);
        if (h == t) {
            return;
        }

        const size_t chunk_len = (h > t) ? (h - t) : (BufferSize - t);

        dma_busy_.store(true, std::memory_order_relaxed);
        dma_active_len_ = chunk_len;

        hw_dcache_clean_range(&storage_[t], chunk_len);
        hw_uart_dma_start_transfer(&storage_[t], chunk_len);
    }

    alignas(4) std::array<uint8_t, BufferSize> storage_{};
    std::atomic<size_t> head_{0};
    std::atomic<size_t> tail_{0};
    size_t dma_active_len_{0};
    std::atomic<bool> dma_busy_{false};
    std::atomic<uint32_t> dropped_bytes_{0};
};
```
:::

## Пастки реалізації та апаратні крайові випадки

1. **Узгодженість кешу даних (D-Cache Coherency).** На високопродуктивних ядрах (Cortex-M7, Cortex-M55) увімкнений D-Cache створює ситуацію, коли ядро оновило байти в кеші, але в фізичну пам'ять SRAM вони ще не скинуті. Якщо контролер DMA починає читати пам'ять, передаються застарілі байти. Розв'язання: розміщення буфера логера в некешованій області пам'яті (через блок MPU), або обов'язковий виклик очищення кешу `SCB_CleanDCache_by_Addr()` перед передачею адреси в регістри DMA.
2. **Розмір буфера як степінь двійки.** Використання довільного розміру вимагає операції взяття залишку від ділення `%`. На ядрах Cortex-M0/M0+ без апаратного дільника інструкція ділення перетворюється на бібліотечний виклик на десятки тактів у критичній секції. Маска `(SIZE - 1)` гарантує виконання операції за 1 такт.
3. **Гонка станів при перериваннях.** Якщо функція `write()` викликається одночасно з основного циклу `main()` та зсередини переривання таймера, модифікація `head` без блокування переривань призведе до руйнування цілісності буфера. Критична секція `hw_enter_critical()` мусить відключати відповідні маски переривань на час копіювання даних. У системах на базі Cortex-M для цього доцільно використовувати маскування через `__set_BASEPRI()`, щоб блокувати лише низькопріоритетні переривання, зберігаючи роботу критичних контурів керування.
4. **Апаратні бар'єри пам'яті (Memory Barriers).** Компілятор та процесор можуть перевпорядковувати інструкції запису. Перед тим як увімкнути канал DMA записом у регістр `DMA_CCR_EN`, необхідно виконати інструкцію бар'єра синхронізації даних `__DSB()`, щоб гарантувати завершення всіх операцій запису в оперативну пам'ять до того, як контролер DMA виставить перший запит на шину.

## Вимірювання та діагностика навантаження

Для підтвердження неблокуючого характеру логера в коді застосовують вивід GPIO-маркера: пін встановлюється у високий рівень на початку функції `async_logger_write()` і скидається в низький перед поверненням. Осцилограф або логічний аналізатор показує імпульс тривалістю від 4 до 12 мкс (час копіювання даних у RAM) незалежно від довжини рядка, тоді як лінія UART TX продовжує передавати байти протягом кількох мілісекунд у фоні.
