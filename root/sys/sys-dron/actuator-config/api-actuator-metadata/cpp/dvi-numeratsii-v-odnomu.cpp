if (actuator_test.function < 1000) {
    const int first_motor_function = 1;    // з MAVLink ACTUATOR_OUTPUT_FUNCTION
    const int first_servo_function = 33;

    if (function >= first_motor_function && function < first_motor_function + MAX_NUM_MOTORS) {        // 1…12
        function = function - first_motor_function + FUNCTION_MOTOR1;                                  // → 101…112
    } else if (function >= first_servo_function && function < first_servo_function + MAX_NUM_SERVOS) { // 33…47
        function = function - first_servo_function + FUNCTION_SERVO1;                                  // → 201…215
    } else {
        return VEHICLE_CMD_RESULT_UNSUPPORTED;
    }
} else {
    actuator_test.function -= 1000;
}
