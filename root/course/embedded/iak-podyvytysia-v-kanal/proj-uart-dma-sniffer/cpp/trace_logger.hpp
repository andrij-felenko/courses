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
