void CruiseFlightState::update(FlightContext& ctx) {
    if (ctx.battery_voltage < 14.0f) {
        ctx.fsm.transition_to(FlightState::LandNow);
    } else if (ctx.obstacle_detected) {
        ctx.fsm.transition_to(FlightState::CollisionAvoidance);
    } else if (ctx.rc_lost) {
        ctx.fsm.transition_to(FlightState::ReturnToLaunch);
    } else {
        execute_path_following(ctx);
    }
}
