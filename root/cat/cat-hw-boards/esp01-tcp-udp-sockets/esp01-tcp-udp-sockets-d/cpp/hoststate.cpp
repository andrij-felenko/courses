enum class HostState {
    Idle,
    Connecting,
    Connected,
    Sending,
    ErrorRecovery
};

class HostSocketFSM {
private:
    HostState state_ = HostState::Idle;
public:
    void process(const char* rx_buf) {
        switch (state_) {
            case HostState::Idle:
                break;
            case HostState::Connecting:
                if (strstr(rx_buf, "CONNECT")) {
                    state_ = HostState::Connected;
                } else if (strstr(rx_buf, "ERROR")) {
                    state_ = HostState::ErrorRecovery;
                }
                break;
            case HostState::Connected:
                if (strstr(rx_buf, "CLOSED")) {
                    state_ = HostState::ErrorRecovery;
                }
                break;
            case HostState::Sending:
                break;
            case HostState::ErrorRecovery:
                state_ = HostState::Connecting;
                break;
        }
    }
};
