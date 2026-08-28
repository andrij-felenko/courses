enum class DeviceState : uint8_t {
    Offline,
    Connecting,
    Online,
    Measuring,
    Fault
};

enum class DeviceEvent : uint8_t {
    TimerWake,
    NetConnected,
    NetError,
    StartPoll,
    DataReady,
    Reset
};

class FlatFsm {
public:
    void dispatch(DeviceEvent evt) {
        switch (state_) {
            case DeviceState::Offline:
                if (evt == DeviceEvent::TimerWake) {
                    modem_power_on();
                    state_ = DeviceState::Connecting;
                }
                break;

            case DeviceState::Connecting:
                if (evt == DeviceEvent::NetConnected) {
                    state_ = DeviceState::Online;
                } else if (evt == DeviceEvent::NetError) {
                    state_ = DeviceState::Fault;
                }
                break;

            case DeviceState::Online:
                if (evt == DeviceEvent::StartPoll) {
                    sensor_trigger();
                    state_ = DeviceState::Measuring;
                }
                break;

            case DeviceState::Measuring:
                if (evt == DeviceEvent::DataReady) {
                    telemetry_send();
                    state_ = DeviceState::Online;
                }
                break;

            case DeviceState::Fault:
                if (evt == DeviceEvent::Reset) {
                    system_reboot();
                }
                break;
        }
    }

private:
    DeviceState state_{DeviceState::Offline};
};
