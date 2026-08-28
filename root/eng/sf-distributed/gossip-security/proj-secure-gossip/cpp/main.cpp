#include <iostream>
#include <vector>
#include <array>
#include <unordered_map>
#include <string_view>
#include <span>
#include <chrono>
#include <expected>
#include <cstring>

namespace gossip::security {

constexpr size_t NodeIdLength = 32;
constexpr size_t SignatureLength = 64;
constexpr size_t MaxPayloadLength = 1024;
constexpr int64_t MaxClockDriftSeconds = 5;

constexpr double ScoreInvalidSignature = -100.0;
constexpr double ScoreEquivocation = -500.0;
constexpr double ScoreValidDelivery = 1.0;
constexpr double ScoreGreylistThreshold = -50.0;

using NodeId = std::array<uint8_t, NodeIdLength>;
using Signature = std::array<uint8_t, SignatureLength>;
using Hash256 = std::array<uint8_t, 32>;

struct NodeIdHash {
    size_t operator()(const NodeId& id) const noexcept {
        size_t h = 0;
        for (size_t i = 0; i < sizeof(size_t) && i < id.size(); ++i) {
            h = (h << 8) | id[i];
        }
        return h;
    }
};

struct GossipEnvelope {
    NodeId originId{};
    uint64_t sequenceNumber{0};
    uint64_t timestampSeconds{0};
    std::vector<uint8_t> payload{};
    Signature signature{};
};

enum class SecurityError {
    PeerBanned,
    PayloadTooLarge,
    ClockDriftExceeded,
    InvalidSignature,
    ReplayStaleSequence,
    EquivocationDetected
};

struct PeerRecord {
    NodeId id{};
    uint64_t lastSequence{0};
    Hash256 lastPayloadHash{};
    double score{0.0};
    bool isBanned{false};
};

class SecureGossipEngine {
public:
    explicit SecureGossipEngine(NodeId localId)
        : localId_(localId) {}

    std::expected<void, SecurityError> processIncomingGossip(
        const NodeId& relayPeerId,
        const GossipEnvelope& envelope,
        std::chrono::seconds currentTime)
    {
        auto& relay = getOrCreatePeer(relayPeerId);
        if (relay.isBanned) {
            return std::unexpected(SecurityError::PeerBanned);
        }

        if (envelope.payload.size() > MaxPayloadLength) {
            relay.score += ScoreInvalidSignature;
            return std::unexpected(SecurityError::PayloadTooLarge);
        }

        // 1. Перевірка часового зсуву
        auto nowSec = static_cast<uint64_t>(currentTime.count());
        int64_t drift = static_cast<int64_t>(envelope.timestampSeconds) - static_cast<int64_t>(nowSec);
        if (drift > MaxClockDriftSeconds || drift < -MaxClockDriftSeconds) {
            return std::unexpected(SecurityError::ClockDriftExceeded);
        }

        // 2. Криптографічна перевірка підпису Ed25519
        if (!verifySignature(envelope.originId, envelope)) {
            relay.score += ScoreInvalidSignature;
            if (relay.score < ScoreGreylistThreshold) {
                relay.isBanned = true;
            }
            return std::unexpected(SecurityError::InvalidSignature);
        }

        auto& origin = getOrCreatePeer(envelope.originId);
        if (origin.isBanned) {
            return std::unexpected(SecurityError::PeerBanned);
        }

        Hash256 currentHash = computeHash(envelope.payload);

        // 3. Перевірка на еквівокацію
        if (envelope.sequenceNumber == origin.lastSequence && origin.lastSequence > 0) {
            if (origin.lastPayloadHash != currentHash) {
                origin.score += ScoreEquivocation;
                origin.isBanned = true;
                relay.score += ScoreInvalidSignature;
                return std::unexpected(SecurityError::EquivocationDetected);
            }
            return std::unexpected(SecurityError::ReplayStaleSequence);
        }

        // 4. Перевірка монотонності послідовності (Replay)
        if (envelope.sequenceNumber < origin.lastSequence) {
            return std::unexpected(SecurityError::ReplayStaleSequence);
        }

        // 5. Оновлення стану
        origin.lastSequence = envelope.sequenceNumber;
        origin.lastPayloadHash = currentHash;
        relay.score += ScoreValidDelivery;

        return {};
    }

    [[nodiscard]] const PeerRecord* getPeer(const NodeId& id) const {
        auto it = peers_.find(id);
        return (it != peers_.end()) ? &it->second : nullptr;
    }

private:
    NodeId localId_;
    std::unordered_map<NodeId, PeerRecord, NodeIdHash> peers_;

    PeerRecord& getOrCreatePeer(const NodeId& id) {
        auto [it, _] = peers_.try_emplace(id, PeerRecord{id, 0, {}, 0.0, false});
        return it->second;
    }

    static Hash256 computeHash(std::span<const uint8_t> payload) {
        Hash256 out{};
        for (size_t i = 0; i < payload.size(); ++i) {
            out[i % 32] ^= payload[i];
        }
        return out;
    }

    static bool verifySignature(const NodeId& /*originId*/, const GossipEnvelope& env) {
        if (!env.signature.empty() && env.signature[0] == 0xFF && env.signature[1] == 0xFF) {
            return false; // Симуляція підробленого підпису
        }
        return true;
    }
};

} // namespace gossip::security

int main() {
    using namespace gossip::security;

    NodeId myId{1};
    NodeId peerA{2};
    NodeId rogueNode{9};

    SecureGossipEngine engine(myId);

    // 1. Коректне повідомлення
    GossipEnvelope msg1{
        .originId = peerA,
        .sequenceNumber = 1,
        .timestampSeconds = 1000,
        .payload = {'S', 't', 'a', 't', 'u', 's', '=', 'O', 'K'},
        .signature = {0xAA}
    };

    auto res1 = engine.processIncomingGossip(peerA, msg1, std::chrono::seconds(1000));
    std::cout << "Message 1 valid: " << (res1.has_value() ? "YES" : "NO") << "\n";

    // 2. Повтор застарілого повідомлення
    auto res2 = engine.processIncomingGossip(peerA, msg1, std::chrono::seconds(1001));
    std::cout << "Replay detected error: "
              << (res2.error() == SecurityError::ReplayStaleSequence ? "Stale Sequence" : "Other") << "\n";

    // 3. Еквівокація (той самий seq=5, різний payload)
    GossipEnvelope rogueMsg1{
        .originId = rogueNode,
        .sequenceNumber = 5,
        .timestampSeconds = 1002,
        .payload = {'V', 'e', 'r', 's', 'i', 'o', 'n', '1'},
        .signature = {0xAA}
    };
    engine.processIncomingGossip(rogueNode, rogueMsg1, std::chrono::seconds(1002));

    GossipEnvelope rogueMsg2{
        .originId = rogueNode,
        .sequenceNumber = 5,
        .timestampSeconds = 1002,
        .payload = {'V', 'e', 'r', 's', 'i', 'o', 'n', '2'},
        .signature = {0xAA}
    };
    auto res3 = engine.processIncomingGossip(rogueNode, rogueMsg2, std::chrono::seconds(1002));
    std::cout << "Equivocation error: "
              << (res3.error() == SecurityError::EquivocationDetected ? "Equivocation Detected" : "Other") << "\n";

    if (const auto* roguePeer = engine.getPeer(rogueNode)) {
        std::cout << "Rogue peer banned: " << (roguePeer->isBanned ? "TRUE" : "FALSE")
                  << ", Score: " << roguePeer->score << "\n";
    }

    return 0;
}
