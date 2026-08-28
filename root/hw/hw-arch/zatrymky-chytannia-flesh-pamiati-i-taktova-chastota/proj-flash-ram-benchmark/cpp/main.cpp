#include <cstdint>
#include <span>
#include <array>

namespace bench {

class DwtCounter {
private:
    static constexpr uintptr_t DemcrAddr  = 0xE000EDFCU;
    static constexpr uintptr_t DwtCtrlAddr = 0xE0001000U;
    static constexpr uintptr_t DwtCycAddr  = 0xE0001004U;

    static constexpr uint32_t TrcenaBit   = 1U << 24;
    static constexpr uint32_t CyccntenaBit = 1U << 0;

public:
    static void init() noexcept {
        *reinterpret_cast<volatile uint32_t*>(DemcrAddr) |= TrcenaBit;
        *reinterpret_cast<volatile uint32_t*>(DwtCycAddr) = 0;
        *reinterpret_cast<volatile uint32_t*>(DwtCtrlAddr) |= CyccntenaBit;
    }

    static uint32_t now() noexcept {
        return *reinterpret_cast<volatile uint32_t*>(DwtCycAddr);
    }
};

struct BenchmarkResults {
    uint32_t cycles_raw_flash{0};
    uint32_t cycles_prefetch{0};
    uint32_t cycles_art_cache{0};
    uint32_t cycles_ram{0};
};

class FlashBenchmark {
private:
    static constexpr uintptr_t FlashAcrAddr = 0x40023C00U;
    static constexpr uint32_t Latency5Ws    = 5U;
    static constexpr uint32_t Prften        = 1U << 8;
    static constexpr uint32_t Icen          = 1U << 9;
    static constexpr uint32_t Dcen          = 1U << 10;
    static constexpr uint32_t Icrst         = 1U << 11;
    static constexpr uint32_t Dcrst         = 1U << 12;

    static auto& acr() noexcept {
        return *reinterpret_cast<volatile uint32_t*>(FlashAcrAddr);
    }

    static constexpr size_t DataSize = 128;
    std::array<int32_t, DataSize> data_a{};
    std::array<int32_t, DataSize> data_b{};

public:
    FlashBenchmark() noexcept {
        for (size_t i = 0; i < DataSize; ++i) {
            data_a[i] = static_cast<int32_t>(i * 17 + 5);
            data_b[i] = static_cast<int32_t>(i * 31 - 12);
        }
    }

    /* Ядро у Flash */
    [[gnu::noinline]]
    static int32_t kernel_flash(std::span<const int32_t> a, std::span<const int32_t> b) noexcept {
        int32_t sum = 0;
        const size_t len = a.size();
        for (size_t i = 0; i < len; ++i) {
            int32_t prod = a[i] * b[i];
            if (prod > 1000) {
                sum += (prod >> 2);
            } else {
                sum -= prod;
            }
        }
        return sum;
    }

    /* Ядро у RAM */
    [[gnu::noinline, gnu::section(".ramfunc")]]
    static int32_t kernel_ram(std::span<const int32_t> a, std::span<const int32_t> b) noexcept {
        int32_t sum = 0;
        const size_t len = a.size();
        for (size_t i = 0; i < len; ++i) {
            int32_t prod = a[i] * b[i];
            if (prod > 1000) {
                sum += (prod >> 2);
            } else {
                sum -= prod;
            }
        }
        return sum;
    }

    BenchmarkResults execute() noexcept {
        BenchmarkResults res;
        volatile int32_t dummy = 0;

        /* 1. Flash 5WS без прискорювачів */
        acr() = Latency5Ws;
        uint32_t t0 = DwtCounter::now();
        dummy += kernel_flash(data_a, data_b);
        res.cycles_raw_flash = DwtCounter::now() - t0;

        /* 2. Flash 5WS з Prefetch */
        acr() = Latency5Ws | Prften;
        t0 = DwtCounter::now();
        dummy += kernel_flash(data_a, data_b);
        res.cycles_prefetch = DwtCounter::now() - t0;

        /* 3. Flash 5WS з ART Cache */
        acr() = Latency5Ws | Prften;
        acr() |= (Icrst | Dcrst);
        acr() &= ~(Icrst | Dcrst);
        acr() |= (Icen | Dcen);

        /* Прогрів кешу */
        dummy += kernel_flash(data_a, data_b);

        t0 = DwtCounter::now();
        dummy += kernel_flash(data_a, data_b);
        res.cycles_art_cache = DwtCounter::now() - t0;

        /* 4. RAM */
        t0 = DwtCounter::now();
        dummy += kernel_ram(data_a, data_b);
        res.cycles_ram = DwtCounter::now() - t0;

        (void)dummy;
        return res;
    }
};

} // namespace bench
