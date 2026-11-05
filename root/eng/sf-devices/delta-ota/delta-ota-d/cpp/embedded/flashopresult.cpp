#include <cstdint>
#include <cstddef>
#include <span>
#include <array>

namespace embedded::hardware {

enum class FlashOpResult : uint8_t {
    Success = 0,
    Busy,
    Timeout,
    AlignmentError,
    HardwareFault
};

/* Апаратні бар'єри упорядкування інструкцій та звернень до пам'яті */
inline void dsb() noexcept {
    __asm__ volatile("dsb 0xF" ::: "memory");
}

inline void isb() noexcept {
    __asm__ volatile("isb 0xF" ::: "memory");
}

/* Безпечний доступ до відображених регістрів периферії з нульовими витратами */
template <typename T, uintptr_t Address>
struct PeripheralReg {
    static void write(T value) noexcept {
        *reinterpret_cast<volatile T*>(Address) = value;
    }
    static T read() noexcept {
        return *reinterpret_cast<volatile T*>(Address);
    }
    static void set_bits(T mask) noexcept {
        write(read() | mask);
    }
    static void clear_bits(T mask) noexcept {
        write(read() & ~mask);
    }
};

class alignas(32) QspiFlashDmaDriver final {
public:
    static constexpr std::size_t kPageSize = 256;
    static constexpr std::size_t kSectorSize = 4096;
    static constexpr std::size_t kCacheLineSize = 32;

    static constexpr uint8_t kCmdWriteEnable = 0x06;
    static constexpr uint8_t kCmdPageProgramQuad = 0x32;
    static constexpr uint8_t kCmdReadStatus = 0x05;
    static constexpr uint8_t kCmdSectorErase4k = 0x20;
    static constexpr uint8_t kStatusWipMask = 0x01;

    explicit QspiFlashDmaDriver(uint32_t base_flash_addr) noexcept
        : base_addr_(base_flash_addr), is_transfer_pending_(false) {}

    void init() noexcept {
        /* Ініціалізація апаратного периферійного модуля QSPI */
        write_qspi_fcr(0x1FU);
        set_qspi_cr_bit(1U << 0); /* Увімкнення контролера */
    }

    [[nodiscard]] FlashOpResult poll_status() noexcept {
        write_qspi_fcr(0x1FU);
        write_qspi_dlr(0);
        write_qspi_ccr((1U << 24) | (1U << 8) | kCmdReadStatus);

        while ((read_qspi_sr() & (1U << 2)) == 0) {
            /* Очікування прапорця FIFO */
        }

        const uint8_t status = static_cast<uint8_t>(read_qspi_dr());
        write_qspi_fcr(0x1FU);

        if ((status & kStatusWipMask) != 0) {
            return FlashOpResult::Busy;
        }
        return FlashOpResult::Success;
    }

    [[nodiscard]] FlashOpResult program_page_async(
        uint32_t offset,
        std::span<const uint8_t, kPageSize> page_data) noexcept {
        
        if (reinterpret_cast<uintptr_t>(page_data.data()) % kCacheLineSize != 0) {
            return FlashOpResult::AlignmentError;
        }

        if (poll_status() == FlashOpResult::Busy) {
            return FlashOpResult::Busy;
        }

        /* Забезпечення узгодженості кеш-пам'яті перед стартом DMA передачі */
        clean_dcache(page_data.data(), kPageSize);

        send_write_enable();

        is_transfer_pending_ = true;

        /* Конфігурація DMA регістра адреси та лічильника */
        setup_dma_stream(page_data.data(), kPageSize);

        /* Налаштування черги QSPI на 4-провідний запис сторінки */
        write_qspi_dlr(kPageSize - 1U);
        write_qspi_ar(base_addr_ + offset);
        set_qspi_cr_bit(1U << 2); /* DMAEN */
        write_qspi_ccr((3U << 24) | (2U << 12) | (1U << 8) | kCmdPageProgramQuad);

        start_dma();
        dsb();

        return FlashOpResult::Busy;
    }

    [[nodiscard]] FlashOpResult erase_sector_4k(uint32_t sector_offset) noexcept {
        if (poll_status() == FlashOpResult::Busy) {
            return FlashOpResult::Busy;
        }

        send_write_enable();

        write_qspi_fcr(0x1FU);
        write_qspi_ar(base_addr_ + sector_offset);
        write_qspi_ccr((2U << 12) | (1U << 8) | kCmdSectorErase4k);

        while ((read_qspi_sr() & (1U << 1)) == 0) {
            /* Очікування завершення передачі інструкції */
        }
        write_qspi_fcr(1U << 1);

        return FlashOpResult::Busy;
    }

    void on_dma_interrupt() noexcept {
        stop_dma();
        clear_qspi_cr_bit(1U << 2); /* Вимикаємо DMAEN */
        is_transfer_pending_ = false;
        isb();
    }

    [[nodiscard]] bool is_transfer_pending() const noexcept {
        return is_transfer_pending_;
    }

private:
    void send_write_enable() noexcept {
        write_qspi_fcr(0x1FU);
        write_qspi_ccr((1U << 8) | kCmdWriteEnable);
        while ((read_qspi_sr() & (1U << 1)) == 0) {
            /* Очікування завершення видачі команди */
        }
        write_qspi_fcr(1U << 1);
    }

    void clean_dcache(const void* addr, std::size_t size) noexcept {
        volatile uint32_t* dccmvac = reinterpret_cast<volatile uint32_t*>(0xE000EF68U);
        uintptr_t start = reinterpret_cast<uintptr_t>(addr) & ~(kCacheLineSize - 1U);
        const uintptr_t end = reinterpret_cast<uintptr_t>(addr) + size;

        while (start < end) {
            *dccmvac = static_cast<uint32_t>(start);
            start += kCacheLineSize;
        }
        dsb();
    }

    /* Допоміжні методи для прямого доступу до регістрів процесорної плати */
    void write_qspi_fcr(uint32_t v) noexcept { *reinterpret_cast<volatile uint32_t*>(0xA000100CU) = v; }
    void write_qspi_dlr(uint32_t v) noexcept { *reinterpret_cast<volatile uint32_t*>(0xA0001010U) = v; }
    void write_qspi_ccr(uint32_t v) noexcept { *reinterpret_cast<volatile uint32_t*>(0xA0001014U) = v; }
    void write_qspi_ar(uint32_t v)  noexcept { *reinterpret_cast<volatile uint32_t*>(0xA0001018U) = v; }
    uint32_t read_qspi_sr() const noexcept   { return *reinterpret_cast<volatile uint32_t*>(0xA0001008U); }
    uint32_t read_qspi_dr() const noexcept   { return *reinterpret_cast<volatile uint32_t*>(0xA0001020U); }
    void set_qspi_cr_bit(uint32_t mask) noexcept { *reinterpret_cast<volatile uint32_t*>(0xA0001000U) |= mask; }
    void clear_qspi_cr_bit(uint32_t mask) noexcept { *reinterpret_cast<volatile uint32_t*>(0xA0001000U) &= ~mask; }

    void setup_dma_stream(const void* src, std::size_t len) noexcept {
        *reinterpret_cast<volatile uint32_t*>(0x40020010U) = reinterpret_cast<uint32_t>(src);
        *reinterpret_cast<volatile uint32_t*>(0x4002000CU) = 0xA0001020U;
        *reinterpret_cast<volatile uint32_t*>(0x40020008U) = static_cast<uint32_t>(len);
        *reinterpret_cast<volatile uint32_t*>(0x40020004U) = (1U << 4) | (1U << 7) | (1U << 1);
    }
    void start_dma() noexcept { *reinterpret_cast<volatile uint32_t*>(0x40020004U) |= 1U; }
    void stop_dma() noexcept  { *reinterpret_cast<volatile uint32_t*>(0x40020004U) &= ~1U; }

    uint32_t base_addr_;
    volatile bool is_transfer_pending_;
};

} // namespace embedded::hardware
