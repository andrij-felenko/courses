#include <cstdint>
#include <span>
#include <expected>
#include <array>
#include <algorithm>
#include <cstring>

namespace proto {

// Бітові прапорці заголовка
enum class flags : uint8_t {
    none     = 0x00,
    ack_req  = 1u << 0,
    is_resp  = 1u << 1,
    is_err   = 1u << 2,
    ext_addr = 1u << 3,
    ver_1    = 1u << 4
};

constexpr flags operator|(flags a, flags b) {
    return static_cast<flags>(static_cast<uint8_t>(a) | static_cast<uint8_t>(b));
}
constexpr bool has_flag(flags val, flags check) {
    return (static_cast<uint8_t>(val) & static_cast<uint8_t>(check)) != 0;
}

// Стандартні протокольні коди помилок
enum class error_code : uint8_t {
    ok              = 0x00,
    invalid_param   = 0x01,
    not_supported   = 0x02,
    busy            = 0x03,
    invalid_state   = 0x04,
    hardware_fault  = 0x05,
    buffer_overflow = 0x06
};

// Типи повідомлень
enum class msg_type : uint8_t {
    cmd_ping            = 0x01,
    cmd_get_telemetry   = 0x10,
    cmd_set_report_rate = 0x20,
    cmd_calibrate_adc   = 0x30
};

// Фіксований бінарний заголовок конверта
#pragma pack(push, 1)
struct header {
    msg_type msg_id;
    flags    flag_bits;
    uint8_t  trans_id;
    uint8_t  src_addr;
    uint8_t  dst_addr;
    uint16_t payload_len;
    uint8_t  reserved{0};
};

struct telemetry_data {
    int16_t  temperature_c_x10;
    uint32_t pressure_pa;
    uint8_t  battery_percent;
};

struct report_rate_config {
    uint16_t rate_ms;
};
#pragma pack(pop)

// Тип функції-обробника з використанням std::expected та std::span
using handler_fn = std::expected<size_t, error_code> (*)(
    std::span<const uint8_t> req_payload,
    std::span<uint8_t> resp_payload
);

struct dispatch_entry {
    msg_type   id;
    size_t     min_req_len;
    handler_fn handler;
};

class sensor_node_dispatcher {
public:
    explicit constexpr sensor_node_dispatcher(uint8_t node_addr)
        : node_addr_(node_addr) {}

    // Обробка вхідного кадру без динамічної пам'яті
    std::span<const uint8_t> process_frame(std::span<const uint8_t> rx_frame,
                                           std::span<uint8_t> tx_buffer) {
        if (rx_frame.size() < sizeof(header)) {
            return {};
        }

        const auto& rx_hdr = *reinterpret_cast<const header*>(rx_frame.data());

        // Фільтрація за адресою
        if (rx_hdr.dst_addr != node_addr_ && rx_hdr.dst_addr != 0x00) {
            return {};
        }

        if (has_flag(rx_hdr.flag_bits, flags::is_resp)) {
            return {}; // Відповіді маршрутизуються клієнту
        }

        bool need_resp = has_flag(rx_hdr.flag_bits, flags::ack_req) && (rx_hdr.dst_addr != 0x00);
        auto rx_payload = rx_frame.subspan(sizeof(header), std::min<size_t>(rx_hdr.payload_len, rx_frame.size() - sizeof(header)));

        if (!need_resp) {
            execute_unconfirmed(rx_hdr.msg_id, rx_payload);
            return {};
        }

        if (tx_buffer.size() < sizeof(header) + 1) {
            return {};
        }

        auto& tx_hdr = *reinterpret_cast<header*>(tx_buffer.data());
        tx_hdr.msg_id = rx_hdr.msg_id;
        tx_hdr.trans_id = rx_hdr.trans_id;
        tx_hdr.src_addr = node_addr_;
        tx_hdr.dst_addr = rx_hdr.src_addr;
        tx_hdr.reserved = 0;

        auto tx_payload = tx_buffer.subspan(sizeof(header));
        auto result = execute_command(rx_hdr.msg_id, rx_payload, tx_payload);

        if (result.has_value()) {
            tx_hdr.flag_bits = flags::is_resp | flags::ver_1;
            tx_hdr.payload_len = static_cast<uint16_t>(result.value());
            return tx_buffer.first(sizeof(header) + result.value());
        } else {
            tx_hdr.flag_bits = flags::is_resp | flags::is_err | flags::ver_1;
            tx_payload[0] = static_cast<uint8_t>(result.error());
            tx_hdr.payload_len = 1;
            return tx_buffer.first(sizeof(header) + 1);
        }
    }

private:
    uint8_t  node_addr_;
    uint16_t report_rate_ms_{1000};
    bool     is_calibrating_{false};

    static std::expected<size_t, error_code> handle_ping(std::span<const uint8_t>, std::span<uint8_t>) {
        return 0;
    }

    std::expected<size_t, error_code> handle_get_telemetry(std::span<const uint8_t>, std::span<uint8_t> resp) {
        if (resp.size() < sizeof(telemetry_data)) {
            return std::unexpected(error_code::buffer_overflow);
        }

        telemetry_data telem{
            .temperature_c_x10 = 245,
            .pressure_pa = 101325,
            .battery_percent = 92
        };
        std::memcpy(resp.data(), &telem, sizeof(telemetry_data));
        return sizeof(telemetry_data);
    }

    std::expected<size_t, error_code> handle_set_report_rate(std::span<const uint8_t> req, std::span<uint8_t>) {
        if (req.size() < sizeof(report_rate_config)) {
            return std::unexpected(error_code::invalid_param);
        }

        report_rate_config cfg{};
        std::memcpy(&cfg, req.data(), sizeof(report_rate_config));

        if (cfg.rate_ms < 100 || cfg.rate_ms > 10000) {
            return std::unexpected(error_code::invalid_param);
        }

        report_rate_ms_ = cfg.rate_ms;
        return 0;
    }

    std::expected<size_t, error_code> handle_calibrate_adc(std::span<const uint8_t>, std::span<uint8_t>) {
        if (is_calibrating_) {
            return std::unexpected(error_code::busy);
        }
        is_calibrating_ = true;
        return 0;
    }

    std::expected<size_t, error_code> execute_command(msg_type type,
                                                      std::span<const uint8_t> req,
                                                      std::span<uint8_t> resp) {
        switch (type) {
            case msg_type::cmd_ping:
                return handle_ping(req, resp);
            case msg_type::cmd_get_telemetry:
                return handle_get_telemetry(req, resp);
            case msg_type::cmd_set_report_rate:
                return handle_set_report_rate(req, resp);
            case msg_type::cmd_calibrate_adc:
                return handle_calibrate_adc(req, resp);
            default:
                return std::unexpected(error_code::not_supported);
        }
    }

    void execute_unconfirmed(msg_type type, std::span<const uint8_t> req) {
        std::array<uint8_t, 1> dummy{};
        (void)execute_command(type, req, dummy);
    }
};

} // namespace proto
