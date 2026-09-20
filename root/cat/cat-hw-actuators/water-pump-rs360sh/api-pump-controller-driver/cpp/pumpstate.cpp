// Статуси та методи відновлення на C++
enum class PumpState {
    Ready = 0,
    Pumping,
    FaultTimeout,
    FaultEmergency
};

struct PumpStatus {
    PumpState state;
    float     dispensedMl;
    uint32_t  remainingMs;
};

class WaterPump {
public:
    PumpStatus getStatus() const;
    Error      resetFault();
};
