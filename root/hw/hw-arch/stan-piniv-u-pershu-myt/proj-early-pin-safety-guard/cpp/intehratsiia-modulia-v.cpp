// Конфігурація для C++20 системи
inline constexpr std::array<SystemSafety::PinConfig, 3> kSystemSafetyPins = {{
    { 0x48000000UL, 5, SystemSafety::HardwareLineExpectation::HardPullDown, SystemSafety::TargetState::OutputInactiveLow, true },
    { 0x48000000UL, 6, SystemSafety::HardwareLineExpectation::HardPullDown, SystemSafety::TargetState::OutputInactiveLow, true },
    { 0x48000400UL, 2, SystemSafety::HardwareLineExpectation::HardPullUp,   SystemSafety::TargetState::Input,             false }
}};

extern "C" void System_EarlySafetyEntry(void) {
    auto result = SystemSafety::PinIntegrityGuard::verify_and_arm(kSystemSafetyPins);
    if (!result.has_value()) {
        SystemSafety::PinIntegrityGuard::execute_emergency_shutdown(result.error());
    }
}
