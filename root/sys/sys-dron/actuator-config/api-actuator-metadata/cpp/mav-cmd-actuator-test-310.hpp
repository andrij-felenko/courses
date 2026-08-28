// покрутити Motor 1 (функція PX4 = 101) на 30 % тяги протягом секунди
vehicle->sendMavCommand(MAV_COMP_ID_AUTOPILOT1, MAV_CMD_ACTUATOR_TEST,
                        true,          // showError
                        0.3f,          // param1: значення
                        1.0f,          // param2: термін, с
                        0, 0,
                        1000 + 101,    // param5: функція зі зсувом
                        0, 0);

// відпустити
vehicle->sendMavCommand(MAV_COMP_ID_AUTOPILOT1, MAV_CMD_ACTUATOR_TEST,
                        true, NAN, 0.0f, 0, 0, 1000 + 101, 0, 0);
