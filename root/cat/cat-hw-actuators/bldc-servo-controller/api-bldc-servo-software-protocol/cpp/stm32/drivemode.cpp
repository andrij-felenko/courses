#include <cstdint>

enum class DriveMode : int8_t {
    ProfilePosition = 1,
    ProfileVelocity = 3,
    TorqueMode = 4
};

class ServoControllerAPI {
private:
    uint16_t controlword{0};
    DriveMode activeMode{DriveMode::ProfilePosition};
    int32_t targetPosition{0};
    uint32_t profileVelocity{0};

public:
    void setDriveMode(DriveMode mode) {
        activeMode = mode;
    }

    void startPositionMove(int32_t targetCounts, uint32_t velocity) {
        setDriveMode(DriveMode::ProfilePosition);
        targetPosition = targetCounts;
        profileVelocity = velocity;

        // Послідовність переходу CiA 402: Shutdown -> SwitchOn -> EnableOperation
        controlword = 0x0006;
        controlword = 0x0007;
        controlword = 0x000F; // Operation Enabled

        // Тригер нової уставки
        controlword |= (1 << 4); 
    }

    [[nodiscard]] uint16_t getControlword() const { return controlword; }
    [[nodiscard]] int32_t getTargetPosition() const { return targetPosition; }
};
