// Радіус прийняття для поточного вейпойнта, метри.
const float accept_radius_m = 2.0f;            // ~WPNAV_RADIUS

// Горизонтальна відстань від апарата до цілі.
// Для невеликих відрізків (десятки–сотні метрів) пласке наближення
// у метрах достатньо точне; на великих дугах беруть формулу гаверсинуса.
float north_m = (target_lat - cur_lat) * 1e-7f * 111320.0f;
float east_m  = (target_lon - cur_lon) * 1e-7f * 111320.0f
                * cosf(cur_lat * 1e-7f * (float)M_PI / 180.0f);
float dist_m  = sqrtf(north_m * north_m + east_m * east_m);

if (dist_m <= accept_radius_m) {
    mission_index++;                 // точку зараховано — беремо наступний пункт
    load_waypoint(mission_index);    // нова уставка для навігаційного контуру
}
