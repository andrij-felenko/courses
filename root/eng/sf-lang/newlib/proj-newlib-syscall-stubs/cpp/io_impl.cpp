/**
 * @file io_impl.cpp
 * @brief Реалізація потокового введення-виведення для Newlib (C++20)
 */
#include "syscall_stubs.hpp"
#include <array>
#include <cerrno>
#include <cstring>
#include <sys/reent.h>
#include <sys/stat.h>

namespace embedded::sys {

namespace {

template <std::size_t Capacity>
class RingBuffer {
public:
    auto push(std::uint8_t byte) noexcept -> bool {
        const auto next_head = (head_ + 1) % Capacity;
        if (next_head == tail_) {
            return false; // Буфер заповнено
        }
        storage_[head_] = byte;
        head_ = next_head;
        return true;
    }

    auto pop() noexcept -> std::optional<std::uint8_t> {
        if (head_ == tail_) {
            return std::nullopt; // Буфер порожній
        }
        const auto val = storage_[tail_];
        tail_ = (tail_ + 1) % Capacity;
        return val;
    }

    [[nodiscard]] auto is_empty() const noexcept -> bool { return head_ == tail_; }

private:
    std::array<std::uint8_t, Capacity> storage_{};
    volatile std::size_t head_{0};
    volatile std::size_t tail_{0};
};

RingBuffer<UartTxBufferSize> g_tx_buffer;
RingBuffer<UartRxBufferSize> g_rx_buffer;

struct MockUartHardware {
    volatile std::uint32_t ISR;
    volatile std::uint32_t TDR;
    volatile std::uint32_t RDR;
    volatile std::uint32_t CR1;
};

auto* const g_uart_hw = reinterpret_cast<MockUartHardware*>(0x40013800UL);
constexpr std::uint32_t UartStatusTxReady = 1U << 7;
constexpr std::uint32_t UartStatusRxReady = 1U << 5;

} // namespace

void SyscallManager::initialize() noexcept {
    g_tx_buffer = RingBuffer<UartTxBufferSize>{};
    g_rx_buffer = RingBuffer<UartRxBufferSize>{};
}

void SyscallManager::putc_immediate(char c) noexcept {
    while (!(g_uart_hw->ISR & UartStatusTxReady)) {
        // Очікування готовності апаратного регістра TDR
    }
    g_uart_hw->TDR = static_cast<std::uint8_t>(c);
}

void SyscallManager::flush_stdout() noexcept {
    while (auto byte = g_tx_buffer.pop()) {
        putc_immediate(static_cast<char>(*byte));
    }
}

} // namespace embedded::sys

extern "C" {

auto _write_r(struct _reent *r, int fd, const void *buf, size_t count) noexcept -> int {
    using namespace embedded::sys;

    if (fd != 1 && fd != 2) {
        r->_errno = EBADF;
        return -1;
    }

    if (buf == nullptr || count == 0) {
        return 0;
    }

    const auto* byte_ptr = static_cast<const std::uint8_t*>(buf);
    for (std::size_t i = 0; i < count; ++i) {
        const auto c = byte_ptr[i];

        if (c == '\n') {
            if (!g_tx_buffer.push('\r')) {
                SyscallManager::putc_immediate('\r');
            }
        }

        if (!g_tx_buffer.push(c)) {
            SyscallManager::putc_immediate(static_cast<char>(c));
        }
    }

    SyscallManager::flush_stdout();
    return static_cast<int>(count);
}

auto _write(int fd, const char *buf, int len) noexcept -> int {
    return _write_r(_impure_ptr, fd, buf, static_cast<std::size_t>(len));
}

auto _read_r(struct _reent *r, int fd, void *buf, size_t count) noexcept -> int {
    using namespace embedded::sys;

    if (fd != 0) {
        r->_errno = EBADF;
        return -1;
    }

    if (buf == nullptr || count == 0) {
        return 0;
    }

    auto* dest = static_cast<std::uint8_t*>(buf);
    std::size_t read_bytes{0};

    while (read_bytes < count) {
        if (auto val = g_rx_buffer.pop()) {
            auto c = *val;
            if (c == '\r') {
                c = '\n';
            }
            SyscallManager::putc_immediate(static_cast<char>(c));
            dest[read_bytes++] = c;
            if (c == '\n') break;
        } else {
            if (g_uart_hw->ISR & UartStatusRxReady) {
                const auto raw_in = static_cast<std::uint8_t>(g_uart_hw->RDR & 0xFF);
                g_rx_buffer.push(raw_in);
            } else if (read_bytes > 0) {
                break;
            }
        }
    }

    return static_cast<int>(read_bytes);
}

auto _read(int fd, char *buf, int len) noexcept -> int {
    return _read_r(_impure_ptr, fd, buf, static_cast<std::size_t>(len));
}

} // extern "C"
