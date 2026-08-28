#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <expected>
#include <string_view>
#include <cstdint>
#include <cstring>

namespace sdio {

enum class Error {
    InvalidFunction,
    OutOfRange,
    DeviceNotReady,
    CrcMismatch,
    Timeout,
    BusBusy
};

constexpr uint32_t CCCR_SDIO_REV    = 0x00;
constexpr uint32_t CCCR_IO_ENABLE   = 0x02;
constexpr uint32_t CCCR_IO_READY    = 0x03;
constexpr uint32_t CCCR_INT_ENABLE  = 0x04;
constexpr uint32_t CCCR_INT_PENDING = 0x05;
constexpr uint32_t CCCR_BUS_IF_CTRL = 0x07;

constexpr uint32_t FBR_BLK_SIZE_L   = 0x110;
constexpr uint32_t FBR_BLK_SIZE_H   = 0x111;

constexpr uint32_t FUNC1_RX_FIFO    = 0x00050;

/* ── 1. Емулятор апаратної частини SDIO-периферії ─────────────────────────── */
class SdioDeviceSim {
public:
    SdioDeviceSim() {
        cccr_.fill(0);
        func1_regs_.fill(0);
        rx_fifo_.fill(0);
        cccr_[CCCR_SDIO_REV] = 0x32; /* SDIO 3.00, CCCR 2.00 */
    }

    std::expected<uint8_t, Error> cmd52(bool write, uint8_t func, uint32_t addr, uint8_t val) {
        if (func == 0) {
            if (addr >= cccr_.size()) return std::unexpected(Error::OutOfRange);
            if (write) {
                if (addr == CCCR_IO_ENABLE) {
                    cccr_[CCCR_IO_ENABLE] = val;
                    cccr_[CCCR_IO_READY] |= static_cast<uint8_t>(val & 0xFE);
                } else if (addr == CCCR_INT_ENABLE || addr == CCCR_BUS_IF_CTRL) {
                    cccr_[addr] = val;
                }
            }
            return cccr_[addr];
        } else if (func == 1) {
            if (addr >= func1_regs_.size()) return std::unexpected(Error::OutOfRange);
            if (write) func1_regs_[addr] = val;
            return func1_regs_[addr];
        }
        return std::unexpected(Error::InvalidFunction);
    }

    std::expected<void, Error> cmd53_read(uint8_t func, bool inc_addr, uint32_t addr, std::span<uint8_t> dst) {
        if (func != 1) return std::unexpected(Error::InvalidFunction);

        if (!inc_addr && addr == FUNC1_RX_FIFO) {
            for (auto &byte : dst) {
                if (fifo_tail_ != fifo_head_) {
                    byte = rx_fifo_[fifo_tail_++];
                    if (fifo_tail_ >= rx_fifo_.size()) fifo_tail_ = 0;
                } else {
                    byte = 0x00;
                }
            }
            if (fifo_tail_ == fifo_head_) {
                dat1_irq_ = false;
                cccr_[CCCR_INT_PENDING] &= static_cast<uint8_t>(~0x02);
            }
            return {};
        } else if (inc_addr) {
            if (addr + dst.size() > func1_regs_.size()) return std::unexpected(Error::OutOfRange);
            std::memcpy(dst.data(), &func1_regs_[addr], dst.size());
            return {};
        }
        return std::unexpected(Error::OutOfRange);
    }

    void inject_packet(std::span<const uint8_t> pkt) {
        for (uint8_t b : pkt) {
            rx_fifo_[fifo_head_++] = b;
            if (fifo_head_ >= rx_fifo_.size()) fifo_head_ = 0;
        }
        if (cccr_[CCCR_INT_ENABLE] & 0x02) {
            cccr_[CCCR_INT_PENDING] |= 0x02;
            dat1_irq_ = true;
        }
    }

    [[nodiscard]] bool is_dat1_irq_active() const noexcept { return dat1_irq_; }

private:
    std::array<uint8_t, 256>    cccr_{};
    std::array<uint8_t, 131072> func1_regs_{};
    std::array<uint8_t, 4096>   rx_fifo_{};
    size_t fifo_head_{0};
    size_t fifo_tail_{0};
    bool   dat1_irq_{false};
};

/* ── 2. RAII-обгортка захисту та блокування шини хоста ─────────────────────── */
class SdioHostDriver;

class SdioHostGuard {
public:
    explicit SdioHostGuard(SdioHostDriver &drv);
    ~SdioHostGuard();
    SdioHostGuard(const SdioHostGuard &) = delete;
    SdioHostGuard &operator=(const SdioHostGuard &) = delete;

private:
    SdioHostDriver &drv_;
};

/* ── 3. Клієнтський драйвер хоста на C++ ─────────────────────────────────── */
class SdioHostDriver {
public:
    explicit SdioHostDriver(SdioDeviceSim &dev) : target_(dev) {}

    void lock()   noexcept { locked_ = true; }
    void unlock() noexcept { locked_ = false; }
    [[nodiscard]] bool is_locked() const noexcept { return locked_; }

    std::expected<void, Error> init_device() {
        SdioHostGuard guard(*this);

        auto rev = target_.cmd52(false, 0, CCCR_SDIO_REV, 0);
        if (!rev) return std::unexpected(rev.error());
        std::cout << "[Host C++] SDIO Ревізія: 0x" << std::hex << static_cast<int>(*rev) << std::dec << "\n";

        /* Активація Функції 1 */
        auto en_res = target_.cmd52(true, 0, CCCR_IO_ENABLE, 0x02);
        if (!en_res) return std::unexpected(en_res.error());

        /* Очікування готовності IO_READY */
        bool ready = false;
        for (int i = 0; i < 5; ++i) {
            auto r = target_.cmd52(false, 0, CCCR_IO_READY, 0);
            if (r && (*r & 0x02)) {
                ready = true;
                break;
            }
        }
        if (!ready) return std::unexpected(Error::DeviceNotReady);

        /* Налаштування розміру блока 512 байтів */
        block_size_ = 512;
        target_.cmd52(true, 0, FBR_BLK_SIZE_L, 0x00);
        target_.cmd52(true, 0, FBR_BLK_SIZE_H, 0x02);

        /* Увімкнення переривань */
        target_.cmd52(true, 0, CCCR_INT_ENABLE, 0x03);

        std::cout << "[Host C++] Пристрій налаштовано: Функція 1 готова, BlockSize="
                  << block_size_ << " байтів\n";
        return {};
    }

    void handle_irq() {
        if (!target_.is_dat1_irq_active()) return;

        SdioHostGuard guard(*this);
        auto pending = target_.cmd52(false, 0, CCCR_INT_PENDING, 0);
        if (pending && (*pending & 0x02)) {
            std::array<uint8_t, 512> rx_buf{};
            auto res = target_.cmd53_read(1, false, FUNC1_RX_FIFO, rx_buf);
            if (res) {
                std::string_view sv(reinterpret_cast<char*>(rx_buf.data()));
                std::cout << "[Host C++ IRQ] Отримано пакет через CMD53: \""
                          << sv << "\" (розмір " << sv.size() << " байтів)\n";
            }
        }
    }

private:
    SdioDeviceSim &target_;
    bool          locked_{false};
    uint16_t      block_size_{0};
};

inline SdioHostGuard::SdioHostGuard(SdioHostDriver &drv) : drv_(drv) { drv_.lock(); }
inline SdioHostGuard::~SdioHostGuard() { drv_.unlock(); }

} // namespace sdio

int main() {
    sdio::SdioDeviceSim dev;
    sdio::SdioHostDriver host(dev);

    if (auto res = host.init_device(); !res) {
        std::cerr << "Помилка ініціалізації SDIO\n";
        return 1;
    }

    std::string_view payload = "IEEE 802.11ac Frame: Rate=433Mbps, SNR=32dB, Encryption=WPA3-SAE";
    dev.inject_packet(std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(payload.data()), payload.size() + 1));

    host.handle_irq();
    return 0;
}
