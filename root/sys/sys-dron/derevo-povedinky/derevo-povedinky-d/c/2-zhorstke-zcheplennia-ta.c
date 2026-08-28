void state_cruise_update(flight_ctx_t *ctx) {
    if (ctx->battery_voltage < 14.0f) {
        fsm_transition_to(ctx, STATE_LAND_NOW);
    } else if (ctx->obstacle_detected) {
        fsm_transition_to(ctx, STATE_COLLISION_AVOIDANCE);
    } else if (ctx->rc_lost) {
        fsm_transition_to(ctx, STATE_RTL);
    } else {
        execute_path_following(ctx);
    }
}
