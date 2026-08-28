#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <optional>
#include <cstdint>

namespace bft {

constexpr size_t DigestLength = 32;
using Digest = std::array<uint8_t, DigestLength>;

enum class Phase : uint8_t {
    PrePrepare = 1,
    Prepare    = 2,
    Commit     = 3
};

struct Packet {
    Phase phase;
    uint32_t view;
    uint32_t seq_num;
    Digest digest;
    uint32_t sender_id;
};

struct SlotState {
    uint32_t view{0};
    uint32_t seq_num{0};
    Digest digest{};
    bool has_pre_prepare{false};
    bool prepared{false};
    bool committed{false};
    uint32_t prepare_votes{0};
    uint32_t commit_votes{0};
    std::vector<bool> prepares_mask;
    std::vector<bool> commits_mask;

    explicit SlotState(size_t node_count = 4)
        : prepares_mask(node_count, false),
          commits_mask(node_count, false) {}
};

class Node {
public:
    Node(uint32_t id, uint32_t total_nodes)
        : id_(id),
          total_nodes_(total_nodes),
          f_faults_((total_nodes - 1) / 3),
          current_view_(0),
          slots_(128, SlotState(total_nodes)) {}

    [[nodiscard]] std::optional<Packet> process_pre_prepare(const Packet& pkt) {
        uint32_t expected_primary = current_view_ % total_nodes_;
        if (pkt.sender_id != expected_primary || pkt.view != current_view_) {
            return std::nullopt;
        }

        auto& slot = slots_[pkt.seq_num];
        if (slot.has_pre_prepare) {
            if (slot.digest != pkt.digest) {
                std::cout << "[Вузол " << id_ << "] УВАГА: Виявлено дворушництво лідера на слоті "
                          << pkt.seq_num << "! Ініціація View Change.\n";
            }
            return std::nullopt;
        }

        slot.view = pkt.view;
        slot.seq_num = pkt.seq_num;
        slot.digest = pkt.digest;
        slot.has_pre_prepare = true;
        slot.prepare_votes = 1;
        slot.prepares_mask[id_] = true;

        return Packet{
            .phase = Phase::Prepare,
            .view = current_view_,
            .seq_num = pkt.seq_num,
            .digest = pkt.digest,
            .sender_id = id_
        };
    }

    [[nodiscard]] std::optional<Packet> process_prepare(const Packet& pkt) {
        if (pkt.view != current_view_ || pkt.sender_id >= total_nodes_) {
            return std::nullopt;
        }

        auto& slot = slots_[pkt.seq_num];
        if (!slot.has_pre_prepare || slot.digest != pkt.digest) {
            return std::nullopt;
        }

        if (!slot.prepares_mask[pkt.sender_id]) {
            slot.prepares_mask[pkt.sender_id] = true;
            slot.prepare_votes++;
        }

        uint32_t required_prepares = 2 * f_faults_;
        if (slot.prepare_votes >= required_prepares && !slot.prepared) {
            slot.prepared = true;
            slot.commit_votes = 1;
            slot.commits_mask[id_] = true;

            return Packet{
                .phase = Phase::Commit,
                .view = current_view_,
                .seq_num = pkt.seq_num,
                .digest = pkt.digest,
                .sender_id = id_
            };
        }
        return std::nullopt;
    }

    bool process_commit(const Packet& pkt) {
        if (pkt.view != current_view_ || pkt.sender_id >= total_nodes_) {
            return false;
        }

        auto& slot = slots_[pkt.seq_num];
        if (!slot.prepared || slot.digest != pkt.digest) {
            return false;
        }

        if (!slot.commits_mask[pkt.sender_id]) {
            slot.commits_mask[pkt.sender_id] = true;
            slot.commit_votes++;
        }

        uint32_t commit_quorum = 2 * f_faults_ + 1;
        if (slot.commit_votes >= commit_quorum && !slot.committed) {
            slot.committed = true;
            std::cout << "[Вузол " << id_ << "] Слот " << pkt.seq_num
                      << ": Успішно зафіксовано (Committed-Local). Виконання транзакції!\n";
            return true;
        }
        return false;
    }

private:
    uint32_t id_;
    uint32_t total_nodes_;
    uint32_t f_faults_;
    uint32_t current_view_;
    std::vector<SlotState> slots_;
};

} // namespace bft
