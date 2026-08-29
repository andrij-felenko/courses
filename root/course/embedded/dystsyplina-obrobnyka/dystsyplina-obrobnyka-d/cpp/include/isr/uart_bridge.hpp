// Міст «USART1 → фонове завдання»: верхня й нижня половини одним типом.
#pragma once

#include <atomic>
#include <cstdint>

#include "isr/frame_parser.hpp"
#include "isr/spsc_ring.hpp"

namespace isr {

class UartBridge {
public:
    struct Stats {
        std::uint32_t bytes_received;
        std::uint32_t ring_overflows;
        std::uint32_t hw_overruns;
        std::uint32_t worst_cycles;
    };

    // Створює нижню половину. Виклик мусить статися ДО NVIC_EnableIRQ.
    static void start();

    // Верхня половина. Кличеться з extern "C" USART1_IRQHandler().
    static void handle_irq() noexcept;

    [[nodiscard]] static Stats stats() noexcept;

    [[nodiscard]] static const FrameParser::Counters &frame_counters() noexcept;

private:
    static void consumer_entry(void *arg) noexcept;
    static void apply(std::span<const std::uint8_t> payload) noexcept;

    static SpscRing<std::uint8_t, 256> ring_;

    // Лічильники пише лише обробник, читає лише фон. relaxed достатньо:
    // синхронізувати ними нічого не треба, важлива сама неподільність.
    static std::atomic<std::uint32_t> bytes_received_;
    static std::atomic<std::uint32_t> ring_overflows_;
    static std::atomic<std::uint32_t> hw_overruns_;
    static std::atomic<std::uint32_t> worst_cycles_;

    static FrameParser parser_;
};

} // namespace isr
