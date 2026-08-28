#ifndef GOSSIP_DISSEMINATOR_HPP
#define GOSSIP_DISSEMINATOR_HPP

#include <string>
#include <string_view>
#include <memory>
#include <functional>
#include <optional>
#include <expected>
#include <chrono>

namespace gossip {

enum class ErrorCode {
    InvalidParam = -1,
    BufferOverflow = -2,
    NodeUnknown = -3,
    StaleVersion = -4,
    ChecksumMismatch = -5,
    MtuExceeded = -6,
    NotActive = -7
};

struct Config {
    uint32_t clusterId{0x47530001};
    uint32_t localNodeId{1};
    uint16_t bindPort{7000};
    uint32_t fanoutK{3};
    std::chrono::milliseconds gossipInterval{150};
    std::chrono::milliseconds antiEntropyInterval{1000};
    std::chrono::seconds tombstoneGracePeriod{86400};
    size_t maxPacketSize{1400};
};

struct StateRecord {
    std::string key;
    std::string value;
    uint64_t version{0};
    bool isTombstone{false};
};

using StateCallback = std::function<void(uint32_t nodeId, const StateRecord& record)>;

class Disseminator {
public:
    static std::expected<std::unique_ptr<Disseminator>, ErrorCode> create(const Config& config);

    virtual ~Disseminator() = default;

    virtual std::expected<void, ErrorCode> start() = 0;
    virtual std::expected<void, ErrorCode> stop() = 0;

    virtual void subscribe(StateCallback callback) = 0;

    virtual std::expected<uint64_t, ErrorCode> setValue(std::string_view key, std::string_view value) = 0;
    virtual std::expected<uint64_t, ErrorCode> deleteKey(std::string_view key) = 0;

    virtual std::expected<StateRecord, ErrorCode> getValue(uint32_t nodeId, std::string_view key) const = 0;
};

} // namespace gossip

#endif // GOSSIP_DISSEMINATOR_HPP
