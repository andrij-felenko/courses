#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <atomic>
#include <optional>
#include <algorithm>
#include <iostream>
#include <iomanip>
#include <numeric>

// ============================================================================
// 1. АПАРАТНІ РЕГІСТРИ ТА СТРУКТУРИ CORTEX-M У C++20
// ============================================================================

struct DwtHardwareRegisters {
    volatile uint32_t CTRL;
    volatile uint32_t CYCCNT;
    volatile uint32_t CPICNT;
    volatile uint32_t EXCCNT;
    volatile uint32_t SLEEPCNT;
    volatile uint32_t LSUCNT;
    volatile uint32_t FOLDCNT;
};

struct CoreDebugRegisters {
    volatile uint32_t DHCSR;
    volatile uint32_t DCRSR;
    volatile uint32_t DCRDR;
    volatile uint32_t DEMCR;
};

struct ScbCacheRegisters {
    volatile uint32_t ICIALLU;
    volatile uint32_t reserved0;
    volatile uint32_t BPIALL;
    volatile uint32_t reserved1;
    volatile uint32_t ICIALLUIS;
    volatile uint32_t DCCMVAC;
    volatile uint32_t DCIMVAC;
    volatile uint32_t DCCIMVAC;
};

inline auto* const DWT_REGS = reinterpret_cast<DwtHardwareRegisters*>(0xE0001000);
inline auto* const DEBUG_REGS = reinterpret_cast<CoreDebugRegisters*>(0xE000EDFC);
inline auto* const CACHE_REGS = reinterpret_cast<ScbCacheRegisters*>(0xE000EF50);

inline constexpr uint32_t DEMCR_TRCENA       = (1u << 24);
inline constexpr uint32_t DWT_CTRL_CYCCNTENA = (1u << 0);

// ============================================================================
// 2. МОДЕЛЬ АПАРАТНОЇ ПЕРИФЕРІЇ
// ============================================================================

struct MockPeripheralUart {
    volatile uint32_t SR;
    volatile uint32_t DR;
    volatile uint32_t BRR;
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t CR3;
};

inline constexpr uint32_t UART_FLAG_PE   = (1u << 0);
inline constexpr uint32_t UART_FLAG_FE   = (1u << 1);
inline constexpr uint32_t UART_FLAG_NE   = (1u << 2);
inline constexpr uint32_t UART_FLAG_ORE  = (1u << 3);
inline constexpr uint32_t UART_FLAG_IDLE = (1u << 4);
inline constexpr uint32_t UART_FLAG_RXNE = (1u << 5);
inline constexpr uint32_t UART_FLAG_TC   = (1u << 6);
inline constexpr uint32_t UART_FLAG_TXE  = (1u << 7);

struct MockPeripheralDma {
    volatile uint32_t CR;
    volatile uint32_t NDTR;
    volatile uint32_t PAR;
    volatile uint32_t M0AR;
    volatile uint32_t M1AR;
    volatile uint32_t FCR;
};

inline constexpr uint32_t DMA_FLAG_EN   = (1u << 0);
inline constexpr uint32_t DMA_FLAG_HTIE = (1u << 3);
inline constexpr uint32_t DMA_FLAG_TCIE = (1u << 4);
inline constexpr uint32_t DMA_FLAG_CIRC = (1u << 8);
inline constexpr uint32_t DMA_FLAG_MINC = (1u << 10);
inline constexpr uint32_t DMA_FLAG_PL_H = (1u << 17);

// ============================================================================
// 3. ПОТОКОБЕЗПЕЧНИЙ КІЛЬЦЕВИЙ БУФЕР (LOCK-FREE SPSC FIFO)
// ============================================================================

template <size_t CapacityPowerOfTwo>
class LockFreeSpscFifo {
    static_assert((CapacityPowerOfTwo & (CapacityPowerOfTwo - 1)) == 0, "Capacity must be power of two");
    static constexpr size_t IndexMask = CapacityPowerOfTwo - 1;

private:
    alignas(4) std::array<uint8_t, CapacityPowerOfTwo> data_storage_{};
    alignas(4) std::atomic<size_t> head_idx_{0};
    alignas(4) std::atomic<size_t> tail_idx_{0};
    alignas(4) std::atomic<size_t> overflow_count_{0};

public:
    constexpr LockFreeSpscFifo() noexcept = default;

    [[nodiscard]] bool enqueue_from_isr(uint8_t byte) noexcept {
        const size_t current_head = head_idx_.load(std::memory_order_relaxed);
        const size_t current_tail = tail_idx_.load(std::memory_order_acquire);

        if ((current_head - current_tail) >= CapacityPowerOfTwo) {
            overflow_count_.fetch_add(1, std::memory_order_relaxed);
            return false;
        }

        data_storage_[current_head & IndexMask] = byte;
        head_idx_.store(current_head + 1, std::memory_order_release);
        return true;
    }

    [[nodiscard]] std::optional<uint8_t> dequeue() noexcept {
        const size_t current_tail = tail_idx_.load(std::memory_order_relaxed);
        const size_t current_head = head_idx_.load(std::memory_order_acquire);

        if (current_head == current_tail) {
            return std::nullopt;
        }

        const uint8_t val = data_storage_[current_tail & IndexMask];
        tail_idx_.store(current_tail + 1, std::memory_order_release);
        return val;
    }

    void reset() noexcept {
        head_idx_.store(0, std::memory_order_relaxed);
        tail_idx_.store(0, std::memory_order_relaxed);
        overflow_count_.store(0, std::memory_order_relaxed);
    }

    [[nodiscard]] size_t size() const noexcept {
        const size_t h = head_idx_.load(std::memory_order_relaxed);
        const size_t t = tail_idx_.load(std::memory_order_relaxed);
        return (h >= t) ? (h - t) : 0;
    }
};

// ============================================================================
// 4. ТЕСТОВИЙ РАННЕР ТА КЕРУВАННЯ D-CACHE У C++20
// ============================================================================

class HardwareCacheManager {
public:
    static void flush_to_ram(std::span<const uint8_t> range) noexcept {
        auto start = reinterpret_cast<uintptr_t>(range.data()) & ~uintptr_t{0x1F};
        auto end = (reinterpret_cast<uintptr_t>(range.data()) + range.size() + 0x1F) & ~uintptr_t{0x1F};

        for (uintptr_t p = start; p < end; p += 32) {
            CACHE_REGS->DCCMVAC = static_cast<uint32_t>(p);
        }
        asm volatile ("dsb" ::: "memory");
        asm volatile ("isb" ::: "memory");
    }

    static void invalidate_from_ram(std::span<const uint8_t> range) noexcept {
        auto start = reinterpret_cast<uintptr_t>(range.data()) & ~uintptr_t{0x1F};
        auto end = (reinterpret_cast<uintptr_t>(range.data()) + range.size() + 0x1F) & ~uintptr_t{0x1F};

        for (uintptr_t p = start; p < end; p += 32) {
            CACHE_REGS->DCIMVAC = static_cast<uint32_t>(p);
        }
        asm volatile ("dsb" ::: "memory");
        asm volatile ("isb" ::: "memory");
    }
};

class MicrocontrollerBenchmarkSuite {
private:
    MockPeripheralUart uart_hw_{};
    MockPeripheralDma dma_hw_{};
    LockFreeSpscFifo<8192> fifo_{};
    uint32_t timer_calibration_cycles_{0};

    [[nodiscard]] uint32_t sample_cyccnt() const noexcept {
        auto* cyccnt = reinterpret_cast<volatile uint32_t*>(0xE0001004);
        return *cyccnt;
    }

public:
    void setup() noexcept {
        DEBUG_REGS->DEMCR |= DEMCR_TRCENA;
        DWT_REGS->CTRL |= DWT_CTRL_CYCCNTENA;

        asm volatile ("isb" ::: "memory");
        asm volatile ("dsb" ::: "memory");
        const uint32_t t0 = sample_cyccnt();
        asm volatile ("isb" ::: "memory");
        asm volatile ("dsb" ::: "memory");
        const uint32_t t1 = sample_cyccnt();
        timer_calibration_cycles_ = (t1 >= t0) ? (t1 - t0) : 0;

        uart_hw_.SR = UART_FLAG_TXE | UART_FLAG_TC;
        uart_hw_.DR = 0;
        uart_hw_.BRR = 0x1D4C;
        uart_hw_.CR1 = (1u << 13) | (1u << 3) | (1u << 2);

        dma_hw_.CR = 0;
        dma_hw_.NDTR = 0;
        dma_hw_.PAR = reinterpret_cast<uint32_t>(&uart_hw_.DR);
        dma_hw_.M0AR = 0;
        dma_hw_.FCR = (1u << 2);
    }

    [[nodiscard]] uint32_t profile_polling(std::span<const uint8_t> payload) noexcept {
        asm volatile ("isb" ::: "memory");
        asm volatile ("dsb" ::: "memory");
        const uint32_t start = sample_cyccnt();

        for (const uint8_t byte : payload) {
            while (!(uart_hw_.SR & UART_FLAG_TXE)) {}
            uart_hw_.DR = byte;
            uart_hw_.SR &= ~UART_FLAG_TXE;
            uart_hw_.SR |= UART_FLAG_TXE;
        }

        while (!(uart_hw_.SR & UART_FLAG_TC)) {}

        asm volatile ("dsb" ::: "memory");
        asm volatile ("isb" ::: "memory");
        const uint32_t elapsed = sample_cyccnt() - start;
        return (elapsed > timer_calibration_cycles_) ? (elapsed - timer_calibration_cycles_) : 1;
    }

    [[nodiscard]] uint32_t profile_interrupts(std::span<const uint8_t> payload) noexcept {
        fifo_.reset();

        asm volatile ("isb" ::: "memory");
        asm volatile ("dsb" ::: "memory");
        const uint32_t start = sample_cyccnt();

        for (const uint8_t byte : payload) {
            fifo_.enqueue_from_isr(byte);
        }

        while (auto opt = fifo_.dequeue()) {
            // Симуляція апаратного збереження/відновлення кадру NVIC
            asm volatile (
                "nop\n nop\n nop\n nop\n nop\n nop\n nop\n nop\n"
                "nop\n nop\n nop\n nop\n nop\n nop\n nop\n nop\n"
                "nop\n nop\n nop\n nop\n nop\n nop\n nop\n nop\n"
                "nop\n nop\n nop\n nop\n nop\n nop\n nop\n nop\n"
                ::: "memory"
            );
            uart_hw_.DR = *opt;
            uart_hw_.SR &= ~UART_FLAG_TXE;
            uart_hw_.SR |= UART_FLAG_TXE;
        }

        asm volatile ("dsb" ::: "memory");
        asm volatile ("isb" ::: "memory");
        const uint32_t elapsed = sample_cyccnt() - start;
        return (elapsed > timer_calibration_cycles_) ? (elapsed - timer_calibration_cycles_) : 1;
    }

    [[nodiscard]] uint32_t profile_dma(std::span<const uint8_t> payload) noexcept {
        asm volatile ("isb" ::: "memory");
        asm volatile ("dsb" ::: "memory");
        const uint32_t start = sample_cyccnt();

        dma_hw_.CR &= ~DMA_FLAG_EN;
        asm volatile ("dsb" ::: "memory");

        dma_hw_.PAR = reinterpret_cast<uint32_t>(&uart_hw_.DR);
        dma_hw_.M0AR = reinterpret_cast<uint32_t>(payload.data());
        dma_hw_.NDTR = static_cast<uint32_t>(payload.size());

        HardwareCacheManager::flush_to_ram(payload);

        dma_hw_.CR = DMA_FLAG_MINC | DMA_FLAG_TCIE | DMA_FLAG_PL_H | DMA_FLAG_EN;
        asm volatile ("dsb" ::: "memory");

        // Симуляція апаратного перенесення блоку
        asm volatile (
            "nop\n nop\n nop\n nop\n nop\n nop\n nop\n nop\n"
            "nop\n nop\n nop\n nop\n nop\n nop\n nop\n nop\n"
            ::: "memory"
        );
        dma_hw_.CR &= ~DMA_FLAG_EN;

        asm volatile ("dsb" ::: "memory");
        asm volatile ("isb" ::: "memory");
        const uint32_t elapsed = sample_cyccnt() - start;
        return (elapsed > timer_calibration_cycles_) ? (elapsed - timer_calibration_cycles_) : 1;
    }
};

int main() {
    alignas(32) static std::array<uint8_t, 4096> global_payload{};
    for (size_t i = 0; i < global_payload.size(); ++i) {
        global_payload[i] = static_cast<uint8_t>((i * 7) & 0xFF);
    }

    MicrocontrollerBenchmarkSuite suite;
    suite.setup();

    constexpr std::array<size_t, 7> test_sizes = { 1, 4, 16, 64, 256, 1024, 4096 };
    constexpr size_t NumIterations = 100;

    std::cout << "\n====================================================================================\n";
    std::cout << "  C++20 BENCHMARK: POLLING vs INTERRUPTS vs DMA (ARM CORTEX-M @ 168 MHz)\n";
    std::cout << "====================================================================================\n\n";

    std::cout << "+------------+---------------------------------+---------------------------------+---------------------------------+\n";
    std::cout << "| Розмір (B) |        POLLING (CPU Wait)       |     INTERRUPTS (SPSC FIFO)      |         CIRCULAR DMA (AHB)      |\n";
    std::cout << "|            |  Min/Med/P99 (Cyc) |   CPB (C/B)|  Min/Med/P99 (Cyc) |   CPB (C/B)|  Min/Med/P99 (Cyc) |   CPB (C/B)|\n";
    std::cout << "+------------+--------------------+------------+--------------------+------------+--------------------+------------+\n";

    std::array<uint32_t, NumIterations> raw_samples{};

    for (const size_t sz : test_sizes) {
        const std::span<const uint8_t> slice(global_payload.data(), sz);

        // Polling
        for (size_t i = 0; i < NumIterations; ++i) raw_samples[i] = suite.profile_polling(slice);
        std::sort(raw_samples.begin(), raw_samples.end());
        const uint32_t poll_min = raw_samples.front();
        const uint32_t poll_med = raw_samples[NumIterations / 2];
        const uint32_t poll_p99 = raw_samples[(NumIterations * 99) / 100];
        const double poll_cpb = static_cast<double>(poll_med) / static_cast<double>(sz);

        // Interrupts
        for (size_t i = 0; i < NumIterations; ++i) raw_samples[i] = suite.profile_interrupts(slice);
        std::sort(raw_samples.begin(), raw_samples.end());
        const uint32_t irq_min = raw_samples.front();
        const uint32_t irq_med = raw_samples[NumIterations / 2];
        const uint32_t irq_p99 = raw_samples[(NumIterations * 99) / 100];
        const double irq_cpb = static_cast<double>(irq_med) / static_cast<double>(sz);

        // DMA
        for (size_t i = 0; i < NumIterations; ++i) raw_samples[i] = suite.profile_dma(slice);
        std::sort(raw_samples.begin(), raw_samples.end());
        const uint32_t dma_min = raw_samples.front();
        const uint32_t dma_med = raw_samples[NumIterations / 2];
        const uint32_t dma_p99 = raw_samples[(NumIterations * 99) / 100];
        const double dma_cpb = static_cast<double>(dma_med) / static_cast<double>(sz);

        std::cout << "| " << std::setw(10) << sz
                  << " | " << std::setw(5) << poll_min << "/" << std::setw(5) << poll_med << "/" << std::setw(5) << poll_p99
                  << " | " << std::setw(10) << std::fixed << std::setprecision(2) << poll_cpb
                  << " | " << std::setw(5) << irq_min << "/" << std::setw(5) << irq_med << "/" << std::setw(5) << irq_p99
                  << " | " << std::setw(10) << std::fixed << std::setprecision(2) << irq_cpb
                  << " | " << std::setw(5) << dma_min << "/" << std::setw(5) << dma_med << "/" << std::setw(5) << dma_p99
                  << " | " << std::setw(10) << std::fixed << std::setprecision(2) << dma_cpb
                  << " |\n";
    }
    std::cout << "+------------+--------------------+------------+--------------------+------------+--------------------+------------+\n\n";

    return 0;
}
