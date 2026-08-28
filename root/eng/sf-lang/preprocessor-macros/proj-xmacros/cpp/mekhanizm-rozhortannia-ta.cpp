// Розгорнута форма в C++ містить типізовані мітки перелічення enum class
constexpr const char* telemetry_cmd_to_str_cpp(TelemetryCmd cmd) noexcept {
    switch (cmd) {
        case TelemetryCmd::Ping: return "ping";
        case TelemetryCmd::GetStatus: return "get_status";
        case TelemetryCmd::SetConfig: return "set_config";
        case TelemetryCmd::Reboot: return "reboot";
        default: return "UNKNOWN";
    }
}
