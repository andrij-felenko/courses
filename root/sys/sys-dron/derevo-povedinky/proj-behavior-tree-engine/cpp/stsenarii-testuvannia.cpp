#include <iostream>

using namespace autopilot::bt;

NodeStatus cond_battery_low(Node&, Blackboard& bb) noexcept {
    const auto v = bb.get<float>("bat_volt").value_or(16.0f);
    if (v < 14.0f) {
        std::cout << "  [Condition] Bat Low: " << v << "V < 14.0V -> SUCCESS\n";
        return NodeStatus::Success;
    }
    return NodeStatus::Failure;
}

NodeStatus act_emergency_land(Node&, Blackboard&) noexcept {
    std::cout << "  [Action] LandNow -> Executing emergency descent\n";
    return NodeStatus::Running;
}

void act_emergency_land_halt(Node&, Blackboard&) noexcept {
    std::cout << "  [Halt] LandNow stopped\n";
}

NodeStatus cond_obstacle_near(Node&, Blackboard& bb) noexcept {
    const auto d = bb.get<float>("lidar_dist").value_or(100.0f);
    if (d < 3.0f) {
        std::cout << "  [Condition] Obstacle Near: " << d << "m < 3.0m -> SUCCESS\n";
        return NodeStatus::Success;
    }
    return NodeStatus::Failure;
}

NodeStatus act_avoid_path(Node&, Blackboard&) noexcept {
    std::cout << "  [Action] AvoidPath -> Executing DWA avoidance maneuver\n";
    return NodeStatus::Running;
}

void act_avoid_path_halt(Node&, Blackboard&) noexcept {
    std::cout << "  [Halt] AvoidPath stopped\n";
}

NodeStatus act_takeoff(Node&, Blackboard&) noexcept {
    std::cout << "  [Action] Takeoff -> Reached 30m altitude -> SUCCESS\n";
    return NodeStatus::Success;
}

NodeStatus act_fly_waypoint(Node&, Blackboard&) noexcept {
    std::cout << "  [Action] FlyWp -> Flying to WP#4 (V=12m/s)\n";
    return NodeStatus::Running;
}

void act_fly_waypoint_halt(Node&, Blackboard&) noexcept {
    std::cout << "  [Halt] FlyWp stopped -> Velocity setpoint zeroed\n";
}

NodeStatus act_track_camera(Node&, Blackboard&) noexcept {
    std::cout << "  [Action] TrackCam -> Optical gimbal tracking active\n";
    return NodeStatus::Running;
}

void act_track_camera_halt(Node&, Blackboard&) noexcept {
    std::cout << "  [Halt] TrackCam stopped\n";
}

void run_cpp_simulation() noexcept {
    BehaviorTree tree;

    const uint8_t root = tree.create_node(NodeType::ReactiveFallback);
    const uint8_t seq_failsafe = tree.create_node(NodeType::Sequence);
    const uint8_t seq_avoid = tree.create_node(NodeType::Sequence);
    const uint8_t seq_mission = tree.create_node(NodeType::Sequence);

    tree.add_child(root, seq_failsafe);
    tree.add_child(root, seq_avoid);
    tree.add_child(root, seq_mission);

    const uint8_t c_bat = tree.create_node(NodeType::Condition, cond_battery_low);
    const uint8_t a_land = tree.create_node(NodeType::Action, act_emergency_land, act_emergency_land_halt);
    tree.add_child(seq_failsafe, c_bat);
    tree.add_child(seq_failsafe, a_land);

    const uint8_t c_obs = tree.create_node(NodeType::Condition, cond_obstacle_near);
    const uint8_t a_avoid = tree.create_node(NodeType::Action, act_avoid_path, act_avoid_path_halt);
    tree.add_child(seq_avoid, c_obs);
    tree.add_child(seq_avoid, a_avoid);

    const uint8_t a_takeoff = tree.create_node(NodeType::Action, act_takeoff);
    const uint8_t par_patrol = tree.create_node(NodeType::ParallelMOfN);
    tree.set_parallel_threshold(par_patrol, 2);

    const uint8_t a_fly = tree.create_node(NodeType::Action, act_fly_waypoint, act_fly_waypoint_halt);
    const uint8_t a_cam = tree.create_node(NodeType::Action, act_track_camera, act_track_camera_halt);
    tree.add_child(par_patrol, a_fly);
    tree.add_child(par_patrol, a_cam);

    tree.add_child(seq_mission, a_takeoff);
    tree.add_child(seq_mission, par_patrol);

    tree.set_root(root);

    std::cout << "=== ТАКТ 1: Нормальний політ (Bat=15.5V, Dist=10.0m) ===\n";
    tree.blackboard().set("bat_volt", 15.5f);
    tree.blackboard().set("lidar_dist", 10.0f);
    tree.tick();

    std::cout << "\n=== ТАКТ 2: Виявлено перешкоду (Dist=2.2m) ===\n";
    tree.blackboard().set("lidar_dist", 2.2f);
    tree.tick();

    std::cout << "\n=== ТАКТ 3: Подвійна відмова: Батарея критична (Bat=13.5V, Dist=2.2m) ===\n";
    tree.blackboard().set("bat_volt", 13.5f);
    tree.tick();
}
