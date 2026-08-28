// Приклад виклику бібліотеки в навігаційному потоці польотного контролера (50 Гц)
void navigation_task_step(GeofenceEngine *fence_engine) {
    GeofencePointGeo current_pos;
    GeofenceVelocityNed current_vel;

    // Отримання оцінки стану від розширеного фільтра Калмана (EKF)
    ekf_get_position_wgs84(&current_pos.lat_e7, &current_pos.lon_e7, &current_pos.alt_m);
    ekf_get_velocity_ned(&current_vel.vx, &current_vel.vy, &current_vel.vz);

    GeofenceReport report;
    GeofenceResult res = geofence_update(fence_engine, &current_pos, &current_vel, &report);

    if (res == GEOFENCE_OK) {
        if (report.state == GEOFENCE_STATE_BREACH) {
            // Виконання дії failsafe відповідно до конфігурації
            switch (report.recommended_action) {
                case GEOFENCE_ACTION_BRAKE_HOLD:
                    flight_mode_set(FLIGHT_MODE_BRAKE);
                    break;
                case GEOFENCE_ACTION_RTL:
                case GEOFENCE_ACTION_SMART_RTL:
                    flight_mode_set(FLIGHT_MODE_RTL);
                    break;
                case GEOFENCE_ACTION_LAND:
                    flight_mode_set(FLIGHT_MODE_LAND);
                    break;
                case GEOFENCE_ACTION_TERMINATE:
                    safety_trigger_flight_termination();
                    break;
                default:
                    break;
            }
        } else if (report.state == GEOFENCE_STATE_WARNING) {
            // Обмеження максимальної швидкості джойстика у напрямку межі
            flight_pilot_limit_velocity_towards_boundary(report.distance_to_boundary_m);
        }
    }
}
