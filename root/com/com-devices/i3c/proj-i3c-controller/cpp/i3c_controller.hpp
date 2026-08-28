// i3c_controller.hpp - Ідіоматичний C++20 інтерфейс з RAII та строгими типами
#pragma once

#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>
#include <expected>
#include <algorithm>

namespace mipi::i3c {

enum class Status : uint8_t {
    Ok = 0,
    Nack,
    ArbitrationLost,
    ParityError,
    Timeout,
    NoDevices,
    BufferOverflow
};

struct ProvisionalId {
    uint64_t value : 48;

    [[nodiscard]] constexpr uint16_t vendor_id() const noexcept {
        return static_cast<uint16_t>((value >> 33) & 0x7FFF);
    }
    [[nodiscard]] constexpr uint16_t part_id() const noexcept {
        return static_cast<uint16_t>((value >> 16) & 0xFFFF);
    }
    [[nodiscard]] constexpr uint8_t instance_id() const noexcept {
        return static_cast<uint8_t>((value >> 12) & 0x0F);
    }
};

struct TargetDescriptor {
    ProvisionalId id{};
    uint8_t bcr{0};
    uint8_t dcr{0};
    uint8_t dynamic_address{0};
    bool ibi_capable{false};
    bool ibi_has_payload{false};
};

class BusController {
public:
    static constexpr size_t MaxTargets = 16;
    static constexpr uint8_t BroadcastAddress = 0x7E;
    static constexpr uint8_t StartDynamicAddress = 0x08;

    constexpr BusController() noexcept : next_address_(StartDynamicAddress) {}

    [[nodiscard]] std::expected<size_t, Status> run_dynamic_address_assignment() noexcept {
        targets_count_ = 0;
        next_address_ = StartDynamicAddress;

        // Генерація широкомовної команди ENTDAA (0x07)
        if (auto res = send_broadcast_ccc(0x07); !res) {
            return std::unexpected(res.error());
        }

        while (targets_count_ < MaxTargets) {
            auto target_info = probe_target_provisional_id();
            if (!target_info.has_value()) {
                break; // Усі доступні пристрої отримали адреси
            }

            const uint8_t assigned_addr = next_address_++;
            if (!assign_address_to_winner(assigned_addr)) {
                return std::unexpected(Status::Nack);
            }

            TargetDescriptor desc{
                .id = target_info->id,
                .bcr = target_info->bcr,
                .dcr = target_info->dcr,
                .dynamic_address = assigned_addr,
                .ibi_capable = (target_info->bcr & 0x02) != 0,
                .ibi_has_payload = (target_info->bcr & 0x04) != 0
            };

            targets_[targets_count_++] = desc;
        }

        if (targets_count_ == 0) {
            return std::unexpected(Status::NoDevices);
        }
        return targets_count_;
    }

    [[nodiscard]] std::expected<void, Status> write_sdr(
        uint8_t address, std::span<const uint8_t> data) noexcept 
    {
        if (!start_transfer(address, false)) {
            return std::unexpected(Status::Nack);
        }

        for (uint8_t byte : data) {
            const uint8_t t_bit = calculate_parity_t_bit(byte);
            if (!push_pull_write_byte(byte, t_bit)) {
                send_stop();
                return std::unexpected(Status::ParityError);
            }
        }

        send_stop();
        return {};
    }

    [[nodiscard]] std::expected<size_t, Status> read_sdr(
        uint8_t address, std::span<uint8_t> buffer) noexcept 
    {
        if (!start_transfer(address, true)) {
            return std::unexpected(Status::Nack);
        }

        size_t bytes_read = 0;
        for (auto& slot : buffer) {
            auto [byte, is_last] = push_pull_read_byte();
            slot = byte;
            bytes_read++;
            if (is_last) {
                break;
            }
        }

        send_stop();
        return bytes_read;
    }

    [[nodiscard]] std::span<const TargetDescriptor> active_targets() const noexcept {
        return std::span<const TargetDescriptor>(targets_.data(), targets_count_);
    }

private:
    [[nodiscard]] static constexpr uint8_t calculate_parity_t_bit(uint8_t b) noexcept {
        b ^= b >> 4;
        b ^= b >> 2;
        b ^= b >> 1;
        return static_cast<uint8_t>(~b & 0x01);
    }

    std::expected<void, Status> send_broadcast_ccc(uint8_t ccc_code) noexcept;
    std::optional<TargetDescriptor> probe_target_provisional_id() noexcept;
    bool assign_address_to_winner(uint8_t dyn_addr) noexcept;
    bool start_transfer(uint8_t addr, bool is_read) noexcept;
    bool push_pull_write_byte(uint8_t data, uint8_t t_bit) noexcept;
    std::pair<uint8_t, bool> push_pull_read_byte() noexcept;
    void send_stop() noexcept;

    std::array<TargetDescriptor, MaxTargets> targets_{};
    size_t targets_count_{0};
    uint8_t next_address_{StartDynamicAddress};
};

} // namespace mipi::i3c
