// DeviceTwinRepository.hpp — Абстрактний кодовий шов C++20
#include <string>
#include <expected>
#include <cstdint>

struct StateUpdate {
    std::string device_id;
    std::string payload_json;
    uint64_t timestamp_ms;
};

struct HomeState {
    std::string home_id;
    uint64_t version_seq;
    std::string json_state;
};

enum class TwinError {
    NotFound,
    VersionConflict,
    DatabaseTimeout,
    OutboxFailure
};

class IDeviceTwinRepository {
public:
    virtual ~IDeviceTwinRepository() = default;

    virtual std::expected<HomeState, TwinError> get_home_state(const std::string& home_id) = 0;
    
    virtual std::expected<void, TwinError> update_device_state(
        const std::string& home_id,
        const StateUpdate& update,
        uint64_t expected_version) = 0;
};
