#include "isr/uart_bridge.hpp"

#include "FreeRTOS.h"
#include "task.h"

#include "stm32f4xx.h"
#include "stm32f4xx_ll_usart.h"

#include "isr/timer.hpp"

#include <array>

namespace isr {

SpscRing<std::uint8_t, 256> UartBridge::ring_{};
std::atomic<std::uint32_t> UartBridge::bytes_received_{0};
std::atomic<std::uint32_t> UartBridge::ring_overflows_{0};
std::atomic<std::uint32_t> UartBridge::hw_overruns_{0};
std::atomic<std::uint32_t> UartBridge::worst_cycles_{0};
FrameParser UartBridge::parser_{};

namespace {

constexpr std::uint32_t kTaskStackWords = 384;

TaskHandle_t g_consumer = nullptr;
StaticTask_t g_task_tcb;
std::array<StackType_t, kTaskStackWords> g_task_stack;

} // namespace

// ---------------------------------------------------------------------------
// ВЕРХНЯ ПОЛОВИНА
// ---------------------------------------------------------------------------
void UartBridge::handle_irq() noexcept
{
    const std::uint32_t entry_cycles = DWT->CYCCNT;

    BaseType_t higher_priority_woken = pdFALSE;
    bool signal_consumer = false;

    // ORE розбираємо першим: поки він висить, RXNE більше не зводиться,
    // і обробник перетворюється на нескінченне холосте спрацювання.
    if (LL_USART_IsActiveFlag_ORE(USART1)) {
        LL_USART_ClearFlag_ORE(USART1);
        hw_overruns_.fetch_add(1, std::memory_order_relaxed);
        signal_consumer = true;
    }

    // Цикл обмежений залізом: приймальний регістр один, і читання його
    // спорожнює. Це не очікування — вихід гарантований самим кристалом.
    while (LL_USART_IsActiveFlag_RXNE(USART1) && LL_USART_IsEnabledIT_RXNE(USART1)) {
        const auto byte = static_cast<std::uint8_t>(LL_USART_ReceiveData8(USART1));

        if (ring_.push_from_isr(byte)) {
            bytes_received_.fetch_add(1, std::memory_order_relaxed);
        } else {
            ring_overflows_.fetch_add(1, std::memory_order_relaxed);
        }
        signal_consumer = true;
    }

    if (signal_consumer && g_consumer != nullptr) {
        vTaskNotifyGiveFromISR(g_consumer, &higher_priority_woken);
    }

    const std::uint32_t spent = DWT->CYCCNT - entry_cycles;
    if (spent > worst_cycles_.load(std::memory_order_relaxed)) {
        worst_cycles_.store(spent, std::memory_order_relaxed);
    }

    portYIELD_FROM_ISR(higher_priority_woken);
}

// ---------------------------------------------------------------------------
// НИЖНЯ ПОЛОВИНА
// ---------------------------------------------------------------------------
void UartBridge::apply(std::span<const std::uint8_t> payload) noexcept
{
    // Місце застосунку. span несе довжину із собою, тож окремого аргументу,
    // який можна розсинхронізувати з буфером, тут просто немає.
    if (!payload.empty() && payload.front() == 0x01) {
        static_cast<void>(Timer::ms_since_boot());
    }
}

void UartBridge::consumer_entry(void *arg) noexcept
{
    static_cast<void>(arg);

    std::array<std::uint8_t, 64> batch{};

    for (;;) {
        // Сповіщення без тайм-ауту було б сліпим: раз на секунду прокидаємось
        // навіть у тиші, щоб помітити замовклу лінію.
        static_cast<void>(ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(1000)));

        // Вичерпуємо кільце до дна: поки ми розбирали попередній кадр,
        // обробник міг покласти ще байти й не надіслати другого сповіщення.
        for (;;) {
            const std::span<std::uint8_t> chunk = ring_.drain(batch);
            if (chunk.empty()) {
                break;
            }
            for (const std::uint8_t byte : chunk) {
                if (const auto frame = parser_.feed(byte)) {
                    apply(*frame);
                }
            }
        }
    }
}

void UartBridge::start()
{
    g_consumer = xTaskCreateStatic(&UartBridge::consumer_entry,
                                   "uart-rx",
                                   kTaskStackWords,
                                   nullptr,
                                   configMAX_PRIORITIES - 2,
                                   g_task_stack.data(),
                                   &g_task_tcb);
    configASSERT(g_consumer != nullptr);
}

UartBridge::Stats UartBridge::stats() noexcept
{
    return Stats{
        .bytes_received = bytes_received_.load(std::memory_order_relaxed),
        .ring_overflows = ring_overflows_.load(std::memory_order_relaxed),
        .hw_overruns = hw_overruns_.load(std::memory_order_relaxed),
        .worst_cycles = worst_cycles_.load(std::memory_order_relaxed),
    };
}

const FrameParser::Counters &UartBridge::frame_counters() noexcept
{
    return parser_.counters();
}

} // namespace isr

extern "C" void USART1_IRQHandler()
{
    isr::UartBridge::handle_irq();
}
