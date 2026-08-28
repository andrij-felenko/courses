#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <algorithm>
#include <cstdint>
#include <optional>
#include <array>
#include <span>

namespace replication {

constexpr size_t MAX_NODES = 8;

enum class CausalRelation {
    Identical,
    Dominates,      // Локальний вектор строго новіший
    IsDominated,    // Вхідний вектор строго новіший (пряма заміна)
    Concurrent      // Паралельні зміни (конфлікт)
};

enum class ConflictStrategy {
    LastWriteWins,
    PreserveSiblings,
    FieldMerge
};

struct VersionVector {
    std::array<uint64_t, MAX_NODES> counters{};

    void increment(size_t node_id) noexcept {
        if (node_id < MAX_NODES) {
            ++counters[node_id];
        }
    }

    void merge_with(const VersionVector& other) noexcept {
        for (size_t i = 0; i < MAX_NODES; ++i) {
            counters[i] = std::max(counters[i], other.counters[i]);
        }
    }

    [[nodiscard]] CausalRelation compare_to(const VersionVector& other) const noexcept {
        bool this_greater = false;
        bool other_greater = false;

        for (size_t i = 0; i < MAX_NODES; ++i) {
            if (counters[i] > other.counters[i]) {
                this_greater = true;
            } else if (counters[i] < other.counters[i]) {
                other_greater = true;
            }
        }

        if (!this_greater && !other_greater) return CausalRelation::Identical;
        if (this_greater && !other_greater)  return CausalRelation::Dominates;
        if (!this_greater && other_greater)  return CausalRelation::IsDominated;
        return CausalRelation::Concurrent;
    }
};

struct RecordRevision {
    std::string value;
    VersionVector vv;
    uint64_t timestamp_ms{0};
    uint32_t origin_node{0};
};

class DatabaseRecord {
public:
    explicit DatabaseRecord(std::string key) : key_(std::move(key)) {}

    void local_write(std::string_view new_value, uint32_t node_id, uint64_t now_ms) {
        VersionVector next_vv;
        for (const auto& sibling : siblings_) {
            next_vv.merge_with(sibling.vv);
        }
        next_vv.increment(node_id);

        siblings_.clear();
        siblings_.push_back(RecordRevision{
            .value = std::string(new_value),
            .vv = next_vv,
            .timestamp_ms = now_ms,
            .origin_node = node_id
        });
    }

    bool apply_remote_update(const RecordRevision& incoming, ConflictStrategy strategy) {
        if (siblings_.empty()) {
            siblings_.push_back(incoming);
            return true;
        }

        bool incoming_is_obsolete = true;
        bool any_concurrent = false;
        std::vector<RecordRevision> survived;
        survived.reserve(siblings_.size());

        for (const auto& local : siblings_) {
            const auto relation = local.vv.compare_to(incoming.vv);

            switch (relation) {
                case CausalRelation::Identical:
                case CausalRelation::Dominates:
                    survived.push_back(local);
                    break;

                case CausalRelation::IsDominated:
                    incoming_is_obsolete = false;
                    break;

                case CausalRelation::Concurrent:
                    incoming_is_obsolete = false;
                    any_concurrent = true;
                    survived.push_back(local);
                    break;
            }
        }

        if (incoming_is_obsolete && !any_concurrent) {
            return false; // Відкинуто як застаріле
        }

        if (!any_concurrent && !incoming_is_obsolete) {
            siblings_.clear();
            siblings_.push_back(incoming);
            return true;
        }

        // Розв'язання конфлікту паралельних гілок
        switch (strategy) {
            case ConflictStrategy::LastWriteWins: {
                RecordRevision winner = incoming;
                for (const auto& s : survived) {
                    if (s.timestamp_ms > winner.timestamp_ms ||
                       (s.timestamp_ms == winner.timestamp_ms && s.origin_node > winner.origin_node)) {
                        winner = s;
                    }
                }
                for (const auto& s : survived) {
                    winner.vv.merge_with(s.vv);
                }
                winner.vv.merge_with(incoming.vv);

                siblings_.clear();
                siblings_.push_back(std::move(winner));
                return true;
            }

            case ConflictStrategy::PreserveSiblings: {
                survived.push_back(incoming);
                siblings_ = std::move(survived);
                return true;
            }

            case ConflictStrategy::FieldMerge: {
                RecordRevision merged;
                merged.value = survived.front().value + "+" + incoming.value;
                merged.vv = survived.front().vv;
                merged.vv.merge_with(incoming.vv);
                merged.timestamp_ms = std::max(incoming.timestamp_ms, survived.front().timestamp_ms);
                merged.origin_node = incoming.origin_node;

                siblings_.clear();
                siblings_.push_back(std::move(merged));
                return true;
            }
        }

        return false;
    }

    [[nodiscard]] std::span<const RecordRevision> siblings() const noexcept {
        return siblings_;
    }

    [[nodiscard]] std::string_view key() const noexcept {
        return key_;
    }

private:
    std::string key_;
    std::vector<RecordRevision> siblings_;
};

} // namespace replication
