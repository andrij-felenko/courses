#include <cstdint>

struct DriveStatus {
    bool isFault{false};
    bool isWarning{false};
    bool isTargetReached{false};
    bool overcurrent{false};
    bool overtemp{false};
};

class FaultHandler {
public:
    static DriveStatus analyze(uint16_t statusword, uint16_t alarmRegister) {
        DriveStatus status;
        status.isFault = (statusword & (1 << 3)) != 0;
        status.isWarning = (statusword & (1 << 7)) != 0;
        status.isTargetReached = (statusword & (1 << 10)) != 0;

        if (status.isFault) {
            status.overcurrent = (alarmRegister & (1 << 0)) != 0;
            status.overtemp = (alarmRegister & (1 << 3)) != 0;
        }
        return status;
    }

    static uint16_t createFaultResetControlword() {
        return 0x0080; // Controlword Bit 7 = 1 (Fault Reset)
    }
};
