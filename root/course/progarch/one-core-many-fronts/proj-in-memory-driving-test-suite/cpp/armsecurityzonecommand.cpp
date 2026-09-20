#pragma once

#include <string>

namespace dh::core {

struct ArmSecurityZoneCommand {
    std::string zone_id;
    std::string pin_code;
};

enum class ArmZoneStatus {
    Success,
    InvalidPin,
    SensorOpen,
    ZoneNotFound
};

struct ArmSecurityZoneResult {
    ArmZoneStatus status;
    std::string zone_id;
};

class ArmSecurityZoneUseCase {
public:
    virtual ~ArmSecurityZoneUseCase() = default;
    virtual ArmSecurityZoneResult execute(const ArmSecurityZoneCommand& cmd) = 0;
};

} // namespace dh::core
