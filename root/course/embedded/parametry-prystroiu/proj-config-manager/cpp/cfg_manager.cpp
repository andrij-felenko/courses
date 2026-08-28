// cfg_manager.hpp & cfg_manager.cpp - Ідіоматичний C++20 модуль
#include <iostream>
#include <array>
#include <string_view>
#include <cstring>
#include <span>
#include <expected>
#include <optional>
#include <algorithm>

namespace embedded::config {

inline constexpr std::uint32_t Magic = 0x43464731U; // "CFG1"
inline constexpr std::uint16_t SchemaV1 = 1;
inline constexpr std::uint16_t SchemaV2 = 2;
inline constexpr std::uint16_t CurrentSchema = SchemaV2;
inline constexpr std::size_t FlashSectorSize = 256;
inline constexpr std::uint32_t DefaultTrialTimeoutSeconds = 60;

enum class Error : std::int8_t {
    ValidationFailed = -1,
    TrialActive      = -2,
    NoTrialToCommit  = -3,
    FlashCorrupted   = -4,
    SchemaMismatch   = -5
};

struct [[gnu::packed]] PayloadV1 {
    char wifi_ssid[32];
    char wifi_pass[32];
    std::uint32_t broker_ip;
    std::uint32_t report_interval_s;
};

struct [[gnu::packed]] PayloadV2 {
    char wifi_ssid[32];
    char wifi_pass[32];
    char broker_host[48];
    std::uint16_t broker_port;
    std::uint16_t tls_enable;
    std::uint32_t report_interval_s;
    std::uint32_t conn_timeout_s;
};

struct [[gnu::packed]] Header {
    std::uint32_t magic;
    std::uint16_t schema_version;
    std::uint16_t flags;
    std::uint32_t sequence_number;
    std::uint16_t payload_len;
    std::uint16_t reserved;
    std::uint32_t crc32;
};

class FaultTolerantConfigManager {
public:
    FaultTolerantConfigManager() noexcept {
        flash_slot_a_.fill(0xFF);
        flash_slot_b_.fill(0xFF);
    }

    std::expected<void, Error> initialize() noexcept {
        const auto* hdr_a = reinterpret_cast<const Header*>(flash_slot_a_.data());
        const auto* hdr_b = reinterpret_cast<const Header*>(flash_slot_b_.data());

        const bool a_valid = is_slot_valid(flash_slot_a_);
        const bool b_valid = is_slot_valid(flash_slot_b_);

        if (!a_valid && !b_valid) {
            load_factory_defaults(active_config_);
            return write_to_flash(active_config_, 1);
        }

        const std::span<const std::uint8_t> chosen =
            (a_valid && b_valid) ? ((hdr_a->sequence_number >= hdr_b->sequence_number) ? flash_slot_a_ : flash_slot_b_)
                                 : (a_valid ? flash_slot_a_ : flash_slot_b_);

        const auto* chosen_hdr = reinterpret_cast<const Header*>(chosen.data());
        active_slot_idx_ = (chosen.data() == flash_slot_a_.data()) ? 0 : 1;
        last_seq_ = chosen_hdr->sequence_number;

        const auto* payload_raw = chosen.data() + sizeof(Header);

        if (chosen_hdr->schema_version == SchemaV1) {
            const auto* v1 = reinterpret_cast<const PayloadV1*>(payload_raw);
            migrate_v1_to_v2(*v1, active_config_);
            return write_to_flash(active_config_, last_seq_ + 1);
        } else if (chosen_hdr->schema_version == CurrentSchema) {
            std::memcpy(&active_config_, payload_raw, sizeof(PayloadV2));
            return {};
        }

        load_factory_defaults(active_config_);
        return write_to_flash(active_config_, last_seq_ + 1);
    }

    std::expected<void, Error> start_trial(const PayloadV2& candidate, std::uint32_t timeout_s = DefaultTrialTimeoutSeconds) noexcept {
        if (trial_running_) {
            return std::unexpected(Error::TrialActive);
        }
        if (!validate(candidate)) {
            return std::unexpected(Error::ValidationFailed);
        }

        candidate_config_ = candidate;
        trial_running_ = true;
        trial_timer_sec_ = timeout_s;
        return {};
    }

    std::expected<void, Error> confirm_commit() noexcept {
        if (!trial_running_) {
            return std::unexpected(Error::NoTrialToCommit);
        }

        active_config_ = candidate_config_;
        trial_running_ = false;
        trial_timer_sec_ = 0;
        return write_to_flash(active_config_, last_seq_ + 1);
    }

    void rollback() noexcept {
        trial_running_ = false;
        trial_timer_sec_ = 0;
    }

    void tick_1hz() noexcept {
        if (trial_running_ && trial_timer_sec_ > 0) {
            --trial_timer_sec_;
            if (trial_timer_sec_ == 0) {
                rollback();
            }
        }
    }

    [[nodiscard]] const PayloadV2& active_config() const noexcept {
        return trial_running_ ? candidate_config_ : active_config_;
    }

    [[nodiscard]] bool is_trial_active() const noexcept { return trial_running_; }

private:
    static constexpr std::uint32_t calculate_crc32(std::span<const std::uint8_t> data) noexcept {
        std::uint32_t crc = 0xFFFFFFFFU;
        for (std::uint8_t byte : data) {
            crc ^= byte;
            for (int bit = 0; bit < 8; ++bit) {
                crc = (crc >> 1) ^ (0xEDB88320U & (-(crc & 1)));
            }
        }
        return ~crc;
    }

    static bool is_slot_valid(std::span<const std::uint8_t> slot) noexcept {
        if (slot.size() < sizeof(Header)) return false;
        const auto* hdr = reinterpret_cast<const Header*>(slot.data());
        if (hdr->magic != Magic || hdr->payload_len > slot.size() - sizeof(Header)) return false;

        const auto payload = slot.subspan(sizeof(Header), hdr->payload_len);
        return calculate_crc32(payload) == hdr->crc32;
    }

    static void load_factory_defaults(PayloadV2& cfg) noexcept {
        std::memset(&cfg, 0, sizeof(PayloadV2));
        std::strncpy(cfg.wifi_ssid, "Factory_AP", sizeof(cfg.wifi_ssid) - 1);
        std::strncpy(cfg.wifi_pass, "SecretPass123", sizeof(cfg.wifi_pass) - 1);
        std::strncpy(cfg.broker_host, "mqtt.iot-cloud.internal", sizeof(cfg.broker_host) - 1);
        cfg.broker_port = 8883;
        cfg.tls_enable = 1;
        cfg.report_interval_s = 60;
        cfg.conn_timeout_s = 180;
    }

    static void migrate_v1_to_v2(const PayloadV1& v1, PayloadV2& v2) noexcept {
        std::memset(&v2, 0, sizeof(PayloadV2));
        std::strncpy(v2.wifi_ssid, v1.wifi_ssid, sizeof(v2.wifi_ssid) - 1);
        std::strncpy(v2.wifi_pass, v1.wifi_pass, sizeof(v2.wifi_pass) - 1);

        const auto* ip = reinterpret_cast<const std::uint8_t*>(&v1.broker_ip);
        std::snprintf(v2.broker_host, sizeof(v2.broker_host), "%u.%u.%u.%u", ip[0], ip[1], ip[2], ip[3]);

        v2.broker_port = 8883;
        v2.tls_enable = 1;
        v2.report_interval_s = (v1.report_interval_s >= 1 && v1.report_interval_s <= 86400) ? v1.report_interval_s : 60;
        v2.conn_timeout_s = v2.report_interval_s * 3;
    }

    static bool validate(const PayloadV2& cfg) noexcept {
        if (std::strlen(cfg.wifi_ssid) == 0 || cfg.broker_port == 0) return false;
        if (cfg.report_interval_s == 0 || cfg.report_interval_s > 86400) return false;
        if (cfg.conn_timeout_s <= cfg.report_interval_s) return false;
        return true;
    }

    std::expected<void, Error> write_to_flash(const PayloadV2& cfg, std::uint32_t seq) noexcept {
        const std::uint8_t target_idx = (active_slot_idx_ == 0) ? 1 : 0;
        auto& target_slot = (target_idx == 0) ? flash_slot_a_ : flash_slot_b_;

        Header hdr{
            .magic = Magic,
            .schema_version = CurrentSchema,
            .flags = 0,
            .sequence_number = seq,
            .payload_len = sizeof(PayloadV2),
            .reserved = 0,
            .crc32 = calculate_crc32(std::span<const std::uint8_t>{
                reinterpret_cast<const std::uint8_t*>(&cfg), sizeof(PayloadV2)})
        };

        target_slot.fill(0xFF);
        std::memcpy(target_slot.data(), &hdr, sizeof(Header));
        std::memcpy(target_slot.data() + sizeof(Header), &cfg, sizeof(PayloadV2));

        active_slot_idx_ = target_idx;
        last_seq_ = seq;
        return {};
    }

    alignas(4) std::array<std::uint8_t, FlashSectorSize> flash_slot_a_;
    alignas(4) std::array<std::uint8_t, FlashSectorSize> flash_slot_b_;
    PayloadV2 active_config_{};
    PayloadV2 candidate_config_{};
    bool trial_running_{false};
    std::uint32_t trial_timer_sec_{0};
    std::uint32_t last_seq_{0};
    std::uint8_t active_slot_idx_{0};
};

} // namespace embedded::config
