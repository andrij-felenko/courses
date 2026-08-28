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
