#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>
#include <expected>
#include <memory>

namespace pbft::api {

constexpr size_t DigestLength = 32;
using Digest = std::array<uint8_t, DigestLength>;

enum class Error : int32_t {
    InvalidSignature     = -1,
    InvalidDigest        = -2,
    ViewMismatch         = -3,
    NotPrimary           = -4,
    Equivocation         = -5,
    DuplicateMessage     = -6,
    WatermarkOutOfBounds = -7,
    InsufficientQuorum   = -8,
    CheckpointInvalid    = -9
};

struct PrePrepareMessage {
    uint32_t view{0};
    uint32_t seq_num{0};
    Digest digest{};
    std::span<const uint8_t> payload{};
    uint32_t sender_id{0};
};

struct PrepareMessage {
    uint32_t view{0};
    uint32_t seq_num{0};
    Digest digest{};
    uint32_t sender_id{0};
};

struct CommitMessage {
    uint32_t view{0};
    uint32_t seq_num{0};
    Digest digest{};
    uint32_t sender_id{0};
};

struct ViewChangeMessage {
    uint32_t new_view{0};
    uint32_t last_checkpoint_seq{0};
    Digest state_digest{};
    uint32_t sender_id{0};
};

class IReplicaEngine {
public:
    virtual ~IReplicaEngine() = default;

    virtual std::expected<PrepareMessage, Error>
    on_pre_prepare(const PrePrepareMessage& msg) = 0;

    virtual std::expected<CommitMessage, Error>
    on_prepare(const PrepareMessage& msg) = 0;

    virtual std::expected<bool, Error>
    on_commit(const CommitMessage& msg) = 0;

    virtual std::expected<ViewChangeMessage, Error>
    on_view_change_timer() = 0;

    virtual std::expected<void, Error>
    mark_executed(uint32_t seq_num) = 0;
};

std::unique_ptr<IReplicaEngine> create_replica_engine(uint32_t node_id, uint32_t total_nodes);

} // namespace pbft::api
