// transmitter_cpp.hpp — Ідіоматична обгортка мовою C++
#pragma once
#include <array>
#include <cstdint>
#include <span>
#include "smart_multispectral/mavlink.h"

class MultispectralTransmitter {
public:
    enum class FilterMode : uint8_t {
        Off = 0,
        FourChannel = 1,
        CustomBand = 2
    };

    struct SensorTelemetry {
        uint32_t time_boot_ms;
        float temperature_c;
        std::array<uint16_t, 4> raw_channels;
        FilterMode filter;
        uint8_t status_flags;
        uint32_t frame_counter;
        uint8_t sd_storage_pct;
    };

    MultispectralTransmitter(uint8_t sys_id, uint8_t comp_id)
        : sys_id_(sys_id), comp_id_(comp_id) {}

    template <typename TransmitFn>
    void send_telemetry(const SensorTelemetry& data, TransmitFn&& transmit_fn) {
        mavlink_message_t msg;
        std::array<uint8_t, MAVLINK_MAX_PACKET_LEN> buffer;

        mavlink_msg_multispectral_survey_status_pack(
            sys_id_,
            comp_id_,
            &msg,
            data.time_boot_ms,
            data.temperature_c,
            data.raw_channels.data(),
            static_cast<uint8_t>(data.filter),
            data.status_flags,
            data.frame_counter,
            data.sd_storage_pct
        );

        const uint16_t len = mavlink_msg_to_send_buffer(buffer.data(), &msg);
        transmit_fn(std::span<const uint8_t>(buffer.data(), len));
    }

private:
    uint8_t sys_id_;
    uint8_t comp_id_;
};
