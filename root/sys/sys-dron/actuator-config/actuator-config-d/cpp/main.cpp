if (isArmed() || (_safety.isButtonAvailable() && !_safety.isSafetyOff())) {
    return vehicle_command_ack_s::VEHICLE_CMD_RESULT_DENIED;
}
...
int timeout_ms = static_cast<int>(lroundf(cmd.param2 * 1000.f));

if (timeout_ms <= 0) {
    actuator_test.action = actuator_test_s::ACTION_RELEASE_CONTROL;
} else {
    actuator_test.timeout_ms = timeout_ms;
}

// enforce a timeout and a maximum limit
if (actuator_test.timeout_ms == 0 || actuator_test.timeout_ms > 3000) {
    actuator_test.timeout_ms = 3000;
}
