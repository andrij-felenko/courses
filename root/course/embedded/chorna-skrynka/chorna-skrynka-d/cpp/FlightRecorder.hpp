// FlightRecorder.hpp - Ідіоматичний модуль бортового реєстратора (C++20)
#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <concepts>
#include <algorithm>

namespace embedded::diagnostics {

enum class Subsystem : uint8_t {
    Core   = 0x00,
    Power  = 0x01,
    Nav    = 0x02,
    Motors = 0x03,
    Com    = 0x04
};

enum class Event : uint8_t {
    None        = 0x00,
    StateChange = 0x01,
    BusError    = 0x02,
    WarnThresh  = 0x03,
    CrashPanic  = 0xFF
};

struct alignas(4) FlightEvent {
    uint32_t  timestamp_ms{0};
    Subsystem subsystem{Subsystem::Core};
    Event     event{Event::None};
    uint16_t  fsm_state{0};
    std::array<uint8_t, 6> payload{};
    uint16_t  crc16{0};

    [[nodiscard]] bool verify_crc() const noexcept;
    void compute_and_store_crc() noexcept;
};

template <size_t Capacity = 256>
class FlightRecorder {
public:
    static constexpr uint32_t MagicHeader = 0x424F5831; // 'BOX1'

    void init() noexcept {
        if (magic_ != MagicHeader) {
            magic_ = MagicHeader;
            boot_count_ = 1;
            crash_count_ = 0;
            head_index_ = 0;
            is_frozen_ = false;
            events_.fill(FlightEvent{});
        } else {
            boot_count_++;
            is_frozen_ = false;
        }
    }

    template <typename TPayload>
    void log(Subsystem subsys, Event evt, uint16_t fsm_state, const TPayload& data) noexcept {
        static_assert(sizeof(TPayload) <= 6, "Payload size must not exceed 6 bytes");
        static_assert(std::is_trivially_copyable_v<TPayload>, "Payload must be trivially copyable");

        std::array<uint8_t, 6> raw_bytes{};
        const auto* src_ptr = reinterpret_cast<const uint8_t*>(&data);
        std::copy_n(src_ptr, sizeof(TPayload), raw_bytes.begin());
        log_raw(subsys, evt, fsm_state, raw_bytes);
    }

    void log(Subsystem subsys, Event evt, uint16_t fsm_state = 0) noexcept {
        log_raw(subsys, evt, fsm_state, std::array<uint8_t, 6>{});
    }

    void panic(uint8_t reason_code, uint32_t fault_addr, uint32_t pc) noexcept {
        is_frozen_ = true;
        crash_count_++;

        auto& slot = events_[head_index_];
        slot.timestamp_ms = get_uptime_ms();
        slot.subsystem = Subsystem::Core;
        slot.event = Event::CrashPanic;
        slot.fsm_state = reason_code;

        std::copy_n(reinterpret_cast<const uint8_t*>(&pc), 4, slot.payload.begin());
        std::copy_n(reinterpret_cast<const uint8_t*>(&fault_addr), 2, slot.payload.begin() + 4);

        slot.compute_and_store_crc();
    }

    [[nodiscard]] bool has_crash_dump() const noexcept {
        return (magic_ == MagicHeader && crash_count_ > 0);
    }

    [[nodiscard]] std::span<const FlightEvent> get_events() const noexcept {
        return events_;
    }

    [[nodiscard]] uint32_t boot_count() const noexcept { return boot_count_; }
    [[nodiscard]] uint32_t crash_count() const noexcept { return crash_count_; }
    [[nodiscard]] uint32_t head_index() const noexcept { return head_index_; }

private:
    void log_raw(Subsystem subsys, Event evt, uint16_t fsm, const std::array<uint8_t, 6>& raw_payload) noexcept {
        if (is_frozen_) return;

        uint32_t current_idx = head_index_;
        head_index_ = (current_idx + 1) % Capacity;

        auto& slot = events_[current_idx];
        slot.timestamp_ms = get_uptime_ms();
        slot.subsystem = subsys;
        slot.event = evt;
        slot.fsm_state = fsm;
        slot.payload = raw_payload;
        slot.compute_and_store_crc();
    }

    [[nodiscard]] static uint32_t get_uptime_ms() noexcept;

    uint32_t magic_{0};
    uint32_t boot_count_{0};
    uint32_t crash_count_{0};
    volatile uint32_t head_index_{0};
    volatile bool is_frozen_{false};
    std::array<FlightEvent, Capacity> events_{};
};

} // namespace embedded::diagnostics
