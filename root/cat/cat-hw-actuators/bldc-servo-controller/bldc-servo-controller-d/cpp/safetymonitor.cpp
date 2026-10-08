class SafetyMonitor {
public:
    struct Thresholds {
        float brake_on_volts{56.0f};
        float brake_off_volts{53.0f};
        float max_overvoltage{60.0f};
        float max_temp_celsius{105.0f};
    };

    explicit SafetyMonitor(const Thresholds& th) : th_(th) {}

    void process(float u_bus, float temp_celsius) {
        // Управління Brake Chopper
        if (u_bus >= th_.brake_on_volts) {
            brake_active_ = true;
        } else if (u_bus <= th_.brake_off_volts) {
            brake_active_ = false;
        }

        // Захисне відключення
        if (u_bus >= th_.max_overvoltage) {
            fault_overvoltage_ = true;
            enabled_ = false;
        }
        if (temp_celsius >= th_.max_temp_celsius) {
            fault_overtemp_ = true;
            enabled_ = false;
        }
    }

    bool is_brake_active() const { return brake_active_; }
    bool is_enabled() const { return enabled_; }
    bool has_fault() const { return fault_overvoltage_ || fault_overtemp_; }

private:
    Thresholds th_;
    bool brake_active_{false};
    bool enabled_{true};
    bool fault_overvoltage_{false};
    bool fault_overtemp_{false};
};
