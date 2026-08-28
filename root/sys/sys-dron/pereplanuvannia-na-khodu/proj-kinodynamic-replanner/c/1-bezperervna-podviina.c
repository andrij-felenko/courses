static Trajectory g_trajectories[2];
static volatile int g_active_idx = 0;

/* У потоці планувальника (пріоритет 80): */
void update_active_trajectory(const Replanner *replanner, double t_now,
                              const SphereObstacle *obstacle, Vec3 goal) {
    int next_idx = 1 - g_active_idx;
    replanner_replan(replanner, &g_trajectories[g_active_idx], t_now,
                     obstacle, goal, &g_trajectories[next_idx]);
    __atomic_store_n(&g_active_idx, next_idx, __ATOMIC_RELEASE);
}

/* У високочастотному потоці відправки MAVLink (400 Гц): */
KinematicState get_current_setpoint(double t_current) {
    int cur_idx = __atomic_load_n(&g_active_idx, __ATOMIC_ACQUIRE);
    return trajectory_eval(&g_trajectories[cur_idx], t_current);
}
