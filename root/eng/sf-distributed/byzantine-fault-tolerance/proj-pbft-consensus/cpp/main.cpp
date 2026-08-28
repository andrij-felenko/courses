#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <optional>
#include <string_view>
#include <cstdint>

namespace pbft {

constexpr size_t DigestSize = 32;
using Digest = std::array<uint8_t, DigestSize>;

enum class MessageType : uint8_t {
    PrePrepare = 1,
    Prepare    = 2,
    Commit     = 3
};

struct Message {
    MessageType type;
    uint32_t view;
    uint32_t seq_num;
    Digest digest;
    uint32_t sender_id;
};

struct LogEntry {
    uint32_t view{0};
    uint32_t seq_num{0};
    Digest digest{};
    bool has_pre_prepare{false};
    std::vector<bool> prepares_from;
    std::vector<bool> commits_from;
    uint32_t prepare_count{0};
    uint32_t commit_count{0};
    bool is_prepared{false};
    bool is_committed{false};

    explicit LogEntry(size_t node_count = 4)
        : prepares_from(node_count, false),
          commits_from(node_count, false) {}
};

class ReplicaNode {
public:
    ReplicaNode(uint32_t id, uint32_t total_nodes)
        : node_id_(id),
          total_nodes_(total_nodes),
          max_faults_((total_nodes - 1) / 3),
          current_view_(0),
          log_(64, LogEntry(total_nodes)) {}

    [[nodiscard]] std::optional<Message> handle_pre_prepare(const Message& msg) {
        uint32_t primary_id = current_view_ % total_nodes_;
        if (msg.sender_id != primary_id) {
            std::cout << "[Вузол " << node_id_ << "] Pre-Prepare відхилено: відправник "
                      << msg.sender_id << " не є лідером виду " << current_view_ << "\n";
            return std::nullopt;
        }

        if (msg.view != current_view_ || msg.seq_num >= log_.size()) {
            return std::nullopt;
        }

        auto& entry = log_[msg.seq_num];
        if (entry.has_pre_prepare) {
            if (entry.digest != msg.digest) {
                std::cout << "[Вузол " << node_id_ << "] Зрада лідера: еквівокація на слоті "
                          << msg.seq_num << "! Запуск View Change.\n";
            }
            return std::nullopt;
        }

        entry.view = msg.view;
        entry.seq_num = msg.seq_num;
        entry.digest = msg.digest;
        entry.has_pre_prepare = true;
        entry.prepare_count = 1;
        entry.prepares_from[node_id_] = true;

        return Message{
            .type = MessageType::Prepare,
            .view = current_view_,
            .seq_num = msg.seq_num,
            .digest = msg.digest,
            .sender_id = node_id_
        };
    }

    [[nodiscard]] std::optional<Message> handle_prepare(const Message& msg) {
        if (msg.view != current_view_ || msg.seq_num >= log_.size() || msg.sender_id >= total_nodes_) {
            return std::nullopt;
        }

        auto& entry = log_[msg.seq_num];
        if (!entry.has_pre_prepare || entry.digest != msg.digest) {
            return std::nullopt;
        }

        if (!entry.prepares_from[msg.sender_id]) {
            entry.prepares_from[msg.sender_id] = true;
            entry.prepare_count++;
        }

        uint32_t quorum_needed = 2 * max_faults_;
        if (entry.prepare_count >= quorum_needed && !entry.is_prepared) {
            entry.is_prepared = true;
            entry.commit_count = 1;
            entry.commits_from[node_id_] = true;

            return Message{
                .type = MessageType::Commit,
                .view = current_view_,
                .seq_num = msg.seq_num,
                .digest = msg.digest,
                .sender_id = node_id_
            };
        }
        return std::nullopt;
    }

    bool handle_commit(const Message& msg) {
        if (msg.view != current_view_ || msg.seq_num >= log_.size() || msg.sender_id >= total_nodes_) {
            return false;
        }

        auto& entry = log_[msg.seq_num];
        if (!entry.is_prepared || entry.digest != msg.digest) {
            return false;
        }

        if (!entry.commits_from[msg.sender_id]) {
            entry.commits_from[msg.sender_id] = true;
            entry.commit_count++;
        }

        uint32_t commit_quorum = 2 * max_faults_ + 1;
        if (entry.commit_count >= commit_quorum && !entry.is_committed) {
            entry.is_committed = true;
            std::cout << "[Вузол " << node_id_ << "] Слот " << msg.seq_num
                      << " зафіксовано (Committed-Local)! Стан репліковано.\n";
            return true;
        }
        return false;
    }

private:
    uint32_t node_id_;
    uint32_t total_nodes_;
    uint32_t max_faults_;
    uint32_t current_view_;
    std::vector<LogEntry> log_;
};

} // namespace pbft
