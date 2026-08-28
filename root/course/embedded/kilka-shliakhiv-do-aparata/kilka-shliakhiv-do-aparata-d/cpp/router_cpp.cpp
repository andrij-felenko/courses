// router_cpp.hpp / router_cpp.cpp — Сучасна ідіоматична C++20 реалізація
#include <iostream>
#include <string_view>
#include <vector>
#include <array>
#include <chrono>
#include <optional>
#include <algorithm>
#include <span>

namespace mavlink_router {

using namespace std::chrono_literals;
using Clock = std::chrono::steady_clock;
using TimePoint = Clock::time_point;

enum class LinkRole {
    PrimaryRf,
    BackupLte,
    Satcom
};

enum class LinkState {
    Active,
    Standby,
    Dead
};

struct PacketKey {
    uint8_t sysid{0};
    uint8_t compid{0};
    uint8_t msgid{0};
    uint8_t seq{0};

    constexpr bool operator==(const PacketKey& other) const = default;
};

class Deduplicator {
public:
    static constexpr size_t WindowSize = 256;
    static constexpr auto MaxAge = 2000ms;

    bool is_duplicate(PacketKey key, TimePoint now) {
        for (const auto& [entry_key, timestamp] : history_) {
            if (timestamp.time_since_epoch().count() > 0 &&
                (now - timestamp) < MaxAge &&
                entry_key == key) {
                return true;
            }
        }
        history_[head_] = {key, now};
        head_ = (head_ + 1) % WindowSize;
        return false;
    }

private:
    struct Entry {
        PacketKey key{};
        TimePoint timestamp{};
    };
    std::array<Entry, WindowSize> history_{};
    size_t head_{0};
};

class Link {
public:
    Link(std::string_view name, LinkRole role)
        : name_(name), role_(role) {}

    void on_packet(uint8_t seq, TimePoint now) {
        if (packets_received_ > 0) {
            uint8_t expected = static_cast<uint8_t>(last_seq_ + 1);
            if (seq != expected) {
                packets_lost_ += static_cast<uint8_t>(seq - expected);
            }
        }
        last_seq_ = seq;
        last_packet_time_ = now;
        packets_received_++;

        uint32_t total = packets_received_ + packets_lost_;
        float lq_inst = total > 0 ? (static_cast<float>(packets_received_) / total) * 100.0f : 100.0f;
        lq_smooth_ = 0.2f * lq_inst + 0.8f * lq_smooth_;
    }

    void update_state(TimePoint now, bool is_active) {
        if (now - last_packet_time_ > 1500ms) {
            state_ = LinkState::Dead;
        } else {
            state_ = is_active ? LinkState::Active : LinkState::Standby;
        }
    }

    [[nodiscard]] std::string_view name() const noexcept { return name_; }
    [[nodiscard]] LinkRole role() const noexcept { return role_; }
    [[nodiscard]] LinkState state() const noexcept { return state_; }
    [[nodiscard]] float lq() const noexcept { return lq_smooth_; }

private:
    std::string_view name_;
    LinkRole role_;
    LinkState state_{LinkState::Dead};
    uint8_t last_seq_{0};
    TimePoint last_packet_time_{};
    uint32_t packets_received_{0};
    uint32_t packets_lost_{0};
    float lq_smooth_{100.0f};
};

class FailoverRouter {
public:
    static constexpr float DropThresholdLq = 30.0f;
    static constexpr float RecoveryThresholdLq = 75.0f;
    static constexpr auto HoldOffDuration = 5000ms;

    FailoverRouter() {
        links_.emplace_back("Point-to-Point 915MHz RF", LinkRole::PrimaryRf);
        links_.emplace_back("Cellular 4G/5G LTE VPN", LinkRole::BackupLte);
        links_.emplace_back("Iridium Satcom SBD", LinkRole::Satcom);
    }

    void process_incoming(size_t link_idx, PacketKey key, std::span<const uint8_t> payload, TimePoint now) {
        if (link_idx >= links_.size()) return;

        links_[link_idx].on_packet(key.seq, now);

        if (dedup_.is_duplicate(key, now)) {
            return; // Відкинути дублікат
        }

        if (link_idx == active_link_idx_) {
            forward_to_gcs(key, payload);
        }
    }

    void tick(TimePoint now) {
        for (size_t i = 0; i < links_.size(); ++i) {
            links_[i].update_state(now, i == active_link_idx_);
        }

        auto& primary = links_[0];
        auto& backup  = links_[1];

        if (active_link_idx_ == 0) {
            if (primary.lq() < DropThresholdLq || primary.state() == LinkState::Dead) {
                if (backup.state() != LinkState::Dead) {
                    active_link_idx_ = 1;
                    recovery_start_time_.reset();
                    std::cout << "[FAILOVER] Перемикання на 4G LTE. LQ RF: " << primary.lq() << "%\n";
                }
            }
        } else if (active_link_idx_ == 1) {
            if (primary.state() != LinkState::Dead && primary.lq() >= RecoveryThresholdLq) {
                if (!recovery_start_time_) {
                    recovery_start_time_ = now;
                    std::cout << "[RECOVERY] RF якість > 75%. Старт таймера на 5 с...\n";
                } else if (now - *recovery_start_time_ >= HoldOffDuration) {
                    active_link_idx_ = 0;
                    recovery_start_time_.reset();
                    std::cout << "[FAILBACK] Повернення на основний RF. LQ: " << primary.lq() << "%\n";
                }
            } else {
                recovery_start_time_.reset();
            }
        }
    }

    [[nodiscard]] size_t active_link() const noexcept { return active_link_idx_; }

private:
    void forward_to_gcs(PacketKey key, std::span<const uint8_t> /*payload*/) {
        // Передача очищеного кадру у віртуальний UDP 127.0.0.1:14550 для QGroundControl
    }

    std::vector<Link> links_;
    size_t active_link_idx_{0};
    std::optional<TimePoint> recovery_start_time_{std::nullopt};
    Deduplicator dedup_;
};

} // namespace mavlink_router
