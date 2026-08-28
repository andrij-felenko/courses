// FlightRecorderCore.hpp - Сучасний ідіоматичний реєстратор подій (C++20)
#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <concepts>
#include <algorithm>
#include <type_traits>

namespace embedded::diagnostics {

enum class Subsystem : uint8_t {
    Core     = 0x00,
    Power    = 0x01,
    Nav      = 0x02,
    Actuator = 0x03,
    Comm     = 0x04
};

enum class EventCode : uint8_t {
    None          = 0x00,
    BootOk        = 0x01,
    FsmTransition = 0x02,
    BusNack       = 0x03,
    BusTimeout    = 0x04,
    VoltageWarn   = 0x05,
    TempCritical  = 0x06,
    HardFault     = 0xFE,
    PanicAbort    = 0xFF
};

struct alignas(4) EventFrame {
    uint32_t  timestamp_ms{0};
    Subsystem subsystem{Subsystem::Core};
    EventCode event_code{EventCode::None};
    uint16_t  fsm_state{0};
    std::array<uint8_t, 6> payload{};
    uint16_t  crc16{0};

    [[nodiscard]] bool is_valid() const noexcept {
        return crc16 == compute_crc();
    }

    void update_crc() noexcept {
        crc16 = compute_crc();
    }

private:
    [[nodiscard]] uint16_t compute_crc() const noexcept {
        uint16_t crc = 0xFFFFU;
        const auto* raw = reinterpret_cast<const uint8_t*>(this);
        for (size_t i = 0; i < 14; ++i) {
            crc ^= static_cast<uint16_t>(raw[i]) << 8;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                if (crc & 0x8000U) {
                    crc = (crc << 1) ^ 0x1021U;
                } else {
                    crc = (crc << 1);
                }
            }
        }
        return crc;
    }
};

template <size_t BufferCapacity = 256>
    requires ((BufferCapacity & (BufferCapacity - 1)) == 0) // Ємність має бути ступенем двійки
class FlightRecorderEngine {
public:
    static constexpr uint32_t MagicHeader = 0x424F5831U; // 'BOX1'
    static constexpr uint32_t BufferMask  = BufferCapacity - 1U;

    void init() noexcept {
        if (magic_ != MagicHeader) {
            magic_ = MagicHeader;
            boot_counter_ = 1;
            crash_counter_ = 0;
            head_index_ = 0;
            is_frozen_ = false;
            frames_.fill(EventFrame{});
        } else {
            boot_counter_++;
            is_frozen_ = false;
        }
    }

    template <typename TPayload>
        requires (sizeof(TPayload) <= 6 && std::is_trivially_copyable_v<TPayload>)
    void record(Subsystem subsys, EventCode code, uint16_t fsm, const TPayload& data) noexcept {
        std::array<uint8_t, 6> serialized{};
        const auto* src = reinterpret_cast<const uint8_t*>(&data);
        std::copy_n(src, sizeof(TPayload), serialized.begin());
        record_raw(subsys, code, fsm, serialized);
    }

    void record(Subsystem subsys, EventCode code, uint16_t fsm = 0) noexcept {
        record_raw(subsys, code, fsm, std::array<uint8_t, 6>{});
    }

    void emergency_panic(uint8_t reason, uint32_t pc, uint32_t fault_addr) noexcept {
        is_frozen_ = true;
        crash_counter_++;

        auto& panic_slot = frames_[head_index_];
        panic_slot.timestamp_ms = get_system_uptime();
        panic_slot.subsystem = Subsystem::Core;
        panic_slot.event_code = EventCode::HardFault;
        panic_slot.fsm_state = reason;

        std::copy_n(reinterpret_cast<const uint8_t*>(&pc), 4, panic_slot.payload.begin());
        std::copy_n(reinterpret_cast<const uint8_t*>(&fault_addr), 2, panic_slot.payload.begin() + 4);
        panic_slot.update_crc();
    }

    [[nodiscard]] bool has_crash_dump() const noexcept {
        return magic_ == MagicHeader && crash_counter_ > 0;
    }

    [[nodiscard]] std::span<const EventFrame> get_frames() const noexcept {
        return frames_;
    }

    [[nodiscard]] uint32_t boot_count() const noexcept { return boot_counter_; }
    [[nodiscard]] uint32_t crash_count() const noexcept { return crash_counter_; }
    [[nodiscard]] uint32_t head() const noexcept { return head_index_; }

private:
    void record_raw(Subsystem subsys, EventCode code, uint16_t fsm, const std::array<uint8_t, 6>& data) noexcept {
        if (is_frozen_) return;

        uint32_t current_idx = head_index_;
        head_index_ = (current_idx + 1U) & BufferMask;

        auto& slot = frames_[current_idx];
        slot.timestamp_ms = get_system_uptime();
        slot.subsystem = subsys;
        slot.event_code = code;
        slot.fsm_state = fsm;
        slot.payload = data;
        slot.update_crc();
    }

    [[nodiscard]] static uint32_t get_system_uptime() noexcept;

    uint32_t magic_{0};
    uint32_t boot_counter_{0};
    uint32_t crash_counter_{0};
    volatile uint32_t head_index_{0};
    volatile bool is_frozen_{false};
    std::array<EventFrame, BufferCapacity> frames_{};
};

} // namespace embedded::diagnostics
