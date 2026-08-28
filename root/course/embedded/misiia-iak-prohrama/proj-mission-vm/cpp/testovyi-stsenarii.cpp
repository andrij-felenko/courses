void run_test_mission() {
    using namespace mission;
    MissionVirtualMachine vm;

    const std::array bytecode = {
        Instruction{ .opcode = Opcode::NavTakeoff, .alt_m = 30.0f },
        Instruction{ .opcode = Opcode::JumpIfBatLow, .param1 = 25, .param2 = 7 },
        Instruction{ .opcode = Opcode::NavWaypoint, .lat_1e7 = 504500000, .lon_1e7 = 305200000, .alt_m = 30.0f },
        Instruction{ .opcode = Opcode::CondDistance, .param1 = 30 },
        Instruction{ .opcode = Opcode::DoSetServo, .param1 = 5, .param2 = 1900 },
        Instruction{ .opcode = Opcode::NavWaypoint, .lat_1e7 = 504550000, .lon_1e7 = 305250000, .alt_m = 30.0f },
        Instruction{ .opcode = Opcode::DoJump, .param1 = 1, .param2 = 3 },
        Instruction{ .opcode = Opcode::NavRtl }
    };

    vm.load_program(bytecode);

    Telemetry telem{
        .lat_deg = 50.45f,
        .lon_deg = 30.52f,
        .alt_m = 30.0f,
        .yaw_deg = 0.0f,
        .dist_to_wp_m = 1.0f,
        .battery_soc_pct = 80.0f,
        .wp_reached = true
    };
    ActuatorCommands act{};

    uint32_t sim_time_ms = 0;
    while (vm.status() != VmStatus::Completed) {
        vm.step(telem, act, sim_time_ms);
        sim_time_ms += 20;

        if (sim_time_ms > 2000) {
            telem.battery_soc_pct = 20.0f; // Імітація просідання батареї
        }
    }
}
