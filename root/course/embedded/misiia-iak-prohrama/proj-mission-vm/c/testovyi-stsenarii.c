void run_test_mission(void) {
    mission_vm_t vm;
    mission_vm_init(&vm);

    vm_instruction_t bytecode[] = {
        /* 0 */ { .opcode = OP_NAV_TAKEOFF, .alt_m = 30.0f },
        /* 1 */ { .opcode = OP_JUMP_IF_BAT_LOW, .param1 = 25, .param2 = 7 },
        /* 2 */ { .opcode = OP_NAV_WAYPOINT, .lat_1e7 = 504500000, .lon_1e7 = 305200000, .alt_m = 30.0f },
        /* 3 */ { .opcode = OP_COND_DISTANCE, .param1 = 30 },
        /* 4 */ { .opcode = OP_DO_SET_SERVO, .param1 = 5, .param2 = 1900 },
        /* 5 */ { .opcode = OP_NAV_WAYPOINT, .lat_1e7 = 504550000, .lon_1e7 = 305250000, .alt_m = 30.0f },
        /* 6 */ { .opcode = OP_DO_JUMP, .param1 = 1, .param2 = 3 },
        /* 7 */ { .opcode = OP_NAV_RTL }
    };

    mission_vm_load(&vm, bytecode, sizeof(bytecode) / sizeof(bytecode[0]));

    vm_telemetry_t telem = {
        .lat_deg = 50.45f,
        .lon_deg = 30.52f,
        .alt_m = 30.0f,
        .yaw_deg = 0.0f,
        .dist_to_wp_m = 1.0f,
        .battery_soc_pct = 80.0f,
        .wp_reached = true
    };
    vm_actuators_t act;
    memset(&act, 0, sizeof(act));

    uint32_t sim_time_ms = 0;
    while (vm.status != VM_STATUS_COMPLETED) {
        mission_vm_step(&vm, &telem, &act, sim_time_ms);
        sim_time_ms += 20;

        if (sim_time_ms > 2000) {
            telem.battery_soc_pct = 20.0f; /* Імітація просідання батареї */
        }
    }
}
