#include <iostream>
#include <vector>
#include <unordered_map>
#include <functional>
#include <cstdint>
#include <span>

enum class MessageType : uint8_t {
    Data,
    Marker
};

struct NetworkMessage {
    MessageType type{MessageType::Data};
    uint32_t from_id{0};
    uint32_t to_id{0};
    int32_t payload{0};
};

class SnapshotNode {
public:
    using SendCallback = std::function<void(const NetworkMessage&)>;

    SnapshotNode(uint32_t id, int32_t initial_balance, uint32_t total_peers)
        : id_(id), balance_(initial_balance), total_peers_(total_peers) {}

    [[nodiscard]] uint32_t id() const noexcept { return id_; }
    [[nodiscard]] int32_t balance() const noexcept { return balance_; }
    [[nodiscard]] bool is_state_recorded() const noexcept { return state_recorded_; }
    [[nodiscard]] int32_t snapshot_balance() const noexcept { return snapshot_balance_; }

    [[nodiscard]] std::span<const int32_t> channel_snapshot(uint32_t peer_id) const {
        auto it = recorded_channels_.find(peer_id);
        if (it != recorded_channels_.end()) {
            return it->second;
        }
        return {};
    }

    void initiate_snapshot(const SendCallback& send) {
        state_recorded_ = true;
        snapshot_balance_ = balance_;

        for (uint32_t peer = 0; peer < total_peers_; ++peer) {
            if (peer == id_) continue;

            channel_recording_[peer] = true;
            marker_received_[peer] = false;
            recorded_channels_[peer].clear();

            send({MessageType::Marker, id_, peer, 0});
        }
    }

    void handle_message(const NetworkMessage& msg, const SendCallback& send) {
        const uint32_t src = msg.from_id;

        if (msg.type == MessageType::Marker) {
            if (!state_recorded_) {
                state_recorded_ = true;
                snapshot_balance_ = balance_;

                marker_received_[src] = true;
                channel_recording_[src] = false;
                recorded_channels_[src].clear();

                for (uint32_t peer = 0; peer < total_peers_; ++peer) {
                    if (peer == id_) continue;

                    if (peer != src) {
                        channel_recording_[peer] = true;
                        marker_received_[peer] = false;
                        recorded_channels_[peer].clear();
                    }

                    send({MessageType::Marker, id_, peer, 0});
                }
            } else {
                marker_received_[src] = true;
                channel_recording_[src] = false;
            }
        } else {
            balance_ += msg.payload;

            if (channel_recording_[src]) {
                recorded_channels_[src].push_back(msg.payload);
            }
        }
    }

    [[nodiscard]] bool is_snapshot_complete() const noexcept {
        if (!state_recorded_) return false;
        for (uint32_t peer = 0; peer < total_peers_; ++peer) {
            if (peer != id_ && !marker_received_.contains(peer)) {
                return false;
            }
            if (peer != id_ && !marker_received_.at(peer)) {
                return false;
            }
        }
        return true;
    }

private:
    uint32_t id_;
    int32_t balance_;
    uint32_t total_peers_;

    bool state_recorded_{false};
    int32_t snapshot_balance_{0};

    std::unordered_map<uint32_t, bool> channel_recording_;
    std::unordered_map<uint32_t, bool> marker_received_;
    std::unordered_map<uint32_t, std::vector<int32_t>> recorded_channels_;
};
