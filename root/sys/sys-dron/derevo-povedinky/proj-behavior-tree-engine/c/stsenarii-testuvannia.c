/* Обробники вузлів для тесту */

bt_status_t cond_battery_low(bt_node_t *self, blackboard_t *bb) {
    (void)self;
    float v = 0.0f;
    if (bb_get_float(bb, "bat_volt", &v) && v < 14.0f) {
        printf("  [Condition] Bat Low: %.2fV < 14.0V -> SUCCESS\n", v);
        return BT_STATUS_SUCCESS;
    }
    return BT_STATUS_FAILURE;
}

bt_status_t act_emergency_land(bt_node_t *self, blackboard_t *bb) {
    (void)self;
    (void)bb;
    printf("  [Action] LandNow -> Executing emergency descent\n");
    return BT_STATUS_RUNNING;
}

void act_emergency_land_halt(bt_node_t *self, blackboard_t *bb) {
    (void)self;
    (void)bb;
    printf("  [Halt] LandNow stopped\n");
}

bt_status_t cond_obstacle_near(bt_node_t *self, blackboard_t *bb) {
    (void)self;
    float d = 0.0f;
    if (bb_get_float(bb, "lidar_dist", &d) && d < 3.0f) {
        printf("  [Condition] Obstacle Near: %.2fm < 3.0m -> SUCCESS\n", d);
        return BT_STATUS_SUCCESS;
    }
    return BT_STATUS_FAILURE;
}

bt_status_t act_avoid_path(bt_node_t *self, blackboard_t *bb) {
    (void)self;
    (void)bb;
    printf("  [Action] AvoidPath -> Executing DWA avoidance maneuver\n");
    return BT_STATUS_RUNNING;
}

void act_avoid_path_halt(bt_node_t *self, blackboard_t *bb) {
    (void)self;
    (void)bb;
    printf("  [Halt] AvoidPath stopped\n");
}

bt_status_t act_takeoff(bt_node_t *self, blackboard_t *bb) {
    (void)self;
    (void)bb;
    printf("  [Action] Takeoff -> Reached 30m altitude -> SUCCESS\n");
    return BT_STATUS_SUCCESS;
}

bt_status_t act_fly_waypoint(bt_node_t *self, blackboard_t *bb) {
    (void)self;
    (void)bb;
    printf("  [Action] FlyWp -> Flying to WP#4 (V=12m/s)\n");
    return BT_STATUS_RUNNING;
}

void act_fly_waypoint_halt(bt_node_t *self, blackboard_t *bb) {
    (void)self;
    (void)bb;
    printf("  [Halt] FlyWp stopped -> Velocity setpoint zeroed\n");
}

bt_status_t act_track_camera(bt_node_t *self, blackboard_t *bb) {
    (void)self;
    (void)bb;
    printf("  [Action] TrackCam -> Optical gimbal tracking active\n");
    return BT_STATUS_RUNNING;
}

void act_track_camera_halt(bt_node_t *self, blackboard_t *bb) {
    (void)self;
    (void)bb;
    printf("  [Halt] TrackCam stopped\n");
}

void run_simulation_demo(void) {
    bt_tree_t tree;
    bt_tree_init(&tree);

    /* Побудова топології дерева */
    uint8_t root = bt_create_node(&tree, BT_NODE_REACTIVE_FALLBACK, NULL, NULL);
    uint8_t seq_failsafe = bt_create_node(&tree, BT_NODE_SEQUENCE, NULL, NULL);
    uint8_t seq_avoid = bt_create_node(&tree, BT_NODE_SEQUENCE, NULL, NULL);
    uint8_t seq_mission = bt_create_node(&tree, BT_NODE_SEQUENCE, NULL, NULL);

    bt_add_child(&tree, root, seq_failsafe);
    bt_add_child(&tree, root, seq_avoid);
    bt_add_child(&tree, root, seq_mission);

    /* Гілка Failsafe */
    uint8_t c_bat = bt_create_node(&tree, BT_NODE_CONDITION, cond_battery_low, NULL);
    uint8_t a_land = bt_create_node(&tree, BT_NODE_ACTION, act_emergency_land, act_emergency_land_halt);
    bt_add_child(&tree, seq_failsafe, c_bat);
    bt_add_child(&tree, seq_failsafe, a_land);

    /* Гілка Avoidance */
    uint8_t c_obs = bt_create_node(&tree, BT_NODE_CONDITION, cond_obstacle_near, NULL);
    uint8_t a_avoid = bt_create_node(&tree, BT_NODE_ACTION, act_avoid_path, act_avoid_path_halt);
    bt_add_child(&tree, seq_avoid, c_obs);
    bt_add_child(&tree, seq_avoid, a_avoid);

    /* Гілка Mission */
    uint8_t a_takeoff = bt_create_node(&tree, BT_NODE_ACTION, act_takeoff, NULL);
    uint8_t par_patrol = bt_create_node(&tree, BT_NODE_PARALLEL_M_OF_N, NULL, NULL);
    tree.nodes[par_patrol].threshold_m = 2; /* Обидва процеси паралельні */

    uint8_t a_fly = bt_create_node(&tree, BT_NODE_ACTION, act_fly_waypoint, act_fly_waypoint_halt);
    uint8_t a_cam = bt_create_node(&tree, BT_NODE_ACTION, act_track_camera, act_track_camera_halt);
    bt_add_child(&tree, par_patrol, a_fly);
    bt_add_child(&tree, par_patrol, a_cam);

    bt_add_child(&tree, seq_mission, a_takeoff);
    bt_add_child(&tree, seq_mission, par_patrol);

    tree.root_id = root;

    printf("=== ТАКТ 1: Нормальний політ (Bat=15.5V, Dist=10.0m) ===\n");
    bb_set_float(&tree.bb, "bat_volt", 15.5f);
    bb_set_float(&tree.bb, "lidar_dist", 10.0f);
    bt_tick(&tree);

    printf("\n=== ТАКТ 2: Виявлено перешкоду (Dist=2.2m) ===\n");
    bb_set_float(&tree.bb, "lidar_dist", 2.2f);
    bt_tick(&tree);

    printf("\n=== ТАКТ 3: Подвійна відмова: Батарея критична (Bat=13.5V, Dist=2.2m) ===\n");
    bb_set_float(&tree.bb, "bat_volt", 13.5f);
    bt_tick(&tree);
}
