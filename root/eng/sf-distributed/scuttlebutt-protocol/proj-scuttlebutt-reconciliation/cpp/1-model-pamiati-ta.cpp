#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <cstdint>
#include <optional>
#include <span>

inline constexpr size_t MTU_PAYLOAD_LIMIT = 1200;

struct VersionedValue {
    std::string value;
    uint64_t version{0};
};

struct EndpointState {
    uint64_t generation{0};
    uint64_t max_version{0};
    std::unordered_map<std::string, VersionedValue> attributes;

    void update_attribute(std::string_view key, std::string_view val) {
        ++max_version;
        attributes[std::string(key)] = VersionedValue{std::string(val), max_version};
    }
};

struct GossipDigest {
    std::string node_id;
    uint64_t generation{0};
    uint64_t max_version{0};
};

struct GossipDelta {
    std::string node_id;
    uint64_t generation{0};
    std::string key;
    std::string value;
    uint64_t version{0};
};
