#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAVLINK_MSG_ID_MISSION_ITEM_INT 73

#define MAV_FRAME_GLOBAL_RELATIVE_ALT_INT 3
#define MAV_CMD_NAV_WAYPOINT 16
#define MAV_CMD_NAV_TAKEOFF 22
#define MAV_CMD_NAV_RETURN_TO_LAUNCH 20
#define MAV_CMD_DO_CHANGE_SPEED 178
#define MAV_CMD_DO_SET_CAM_TRIGG_DIST 206
#define MAV_CMD_DO_JUMP 177

#define DEG_TO_RAD (3.14159265358979323846 / 180.0)

typedef struct {
    float param1;
    float param2;
    float param3;
    float param4;
    int32_t x;
    int32_t y;
    float z;
    uint16_t seq;
    uint16_t command;
    uint8_t target_system;
    uint8_t target_component;
    uint8_t frame;
    uint8_t current;
    uint8_t autocontinue;
    uint8_t mission_type;
} mavlink_mission_item_int_t;

static inline int32_t deg_to_degE7(double deg) {
    return (int32_t)llround(deg * 1.0e7);
}

static inline double degE7_to_deg(int32_t degE7) {
    return (double)degE7 * 1.0e-7;
}

// Розрахунок геодезичного зміщення в метрах
void add_meter_offset(double base_lat, double base_lon, double d_north_m, double d_east_m,
                      double *out_lat, double *out_lon) {
    double lat_rad = base_lat * DEG_TO_RAD;
    double m_per_deg_lat = 111132.95;
    double m_per_deg_lon = 111319.5 * cos(lat_rad);

    *out_lat = base_lat + (d_north_m / m_per_deg_lat);
    *out_lon = base_lon + (d_east_m / m_per_deg_lon);
}

mavlink_mission_item_int_t make_takeoff(uint16_t seq, double lat, double lon, float alt_m) {
    mavlink_mission_item_int_t item = {0};
    item.seq = seq;
    item.command = MAV_CMD_NAV_TAKEOFF;
    item.frame = MAV_FRAME_GLOBAL_RELATIVE_ALT_INT;
    item.current = (seq == 0) ? 1 : 0;
    item.autocontinue = 1;
    item.param1 = 0.0f; // Тангаж зльоту
    item.x = deg_to_degE7(lat);
    item.y = deg_to_degE7(lon);
    item.z = alt_m;
    return item;
}

mavlink_mission_item_int_t make_change_speed(uint16_t seq, float speed_m_s) {
    mavlink_mission_item_int_t item = {0};
    item.seq = seq;
    item.command = MAV_CMD_DO_CHANGE_SPEED;
    item.frame = MAV_FRAME_GLOBAL_RELATIVE_ALT_INT;
    item.autocontinue = 1;
    item.param1 = 1.0f; // Groundspeed
    item.param2 = speed_m_s;
    item.param3 = -1.0f; // Throttle без змін
    item.param4 = 0.0f;  // Абсолютна швидкість
    return item;
}

mavlink_mission_item_int_t make_waypoint(uint16_t seq, double lat, double lon, float alt_m,
                                         float hold_time_s, float accept_radius_m, float pass_radius_m) {
    mavlink_mission_item_int_t item = {0};
    item.seq = seq;
    item.command = MAV_CMD_NAV_WAYPOINT;
    item.frame = MAV_FRAME_GLOBAL_RELATIVE_ALT_INT;
    item.autocontinue = 1;
    item.param1 = hold_time_s;
    item.param2 = accept_radius_m;
    item.param3 = pass_radius_m;
    item.param4 = NAN; // Курс за траєкторією
    item.x = deg_to_degE7(lat);
    item.y = deg_to_degE7(lon);
    item.z = alt_m;
    return item;
}

mavlink_mission_item_int_t make_camera_trigger(uint16_t seq, float trigger_dist_m) {
    mavlink_mission_item_int_t item = {0};
    item.seq = seq;
    item.command = MAV_CMD_DO_SET_CAM_TRIGG_DIST;
    item.frame = MAV_FRAME_GLOBAL_RELATIVE_ALT_INT;
    item.autocontinue = 1;
    item.param1 = trigger_dist_m;
    item.param2 = 0.0f;
    item.param3 = 1.0f; // Негайний знімок на вході
    return item;
}

mavlink_mission_item_int_t make_jump(uint16_t seq, uint16_t target_seq, uint16_t repeat_count) {
    mavlink_mission_item_int_t item = {0};
    item.seq = seq;
    item.command = MAV_CMD_DO_JUMP;
    item.frame = MAV_FRAME_GLOBAL_RELATIVE_ALT_INT;
    item.autocontinue = 1;
    item.param1 = (float)target_seq;
    item.param2 = (float)repeat_count;
    return item;
}

mavlink_mission_item_int_t make_rtl(uint16_t seq) {
    mavlink_mission_item_int_t item = {0};
    item.seq = seq;
    item.command = MAV_CMD_NAV_RETURN_TO_LAUNCH;
    item.frame = MAV_FRAME_GLOBAL_RELATIVE_ALT_INT;
    item.autocontinue = 1;
    return item;
}

bool validate_mission(const mavlink_mission_item_int_t *items, size_t count) {
    if (items == NULL || count == 0) {
        printf("Помилка: порожній план місії\n");
        return false;
    }
    for (size_t i = 0; i < count; ++i) {
        if (items[i].seq != i) {
            printf("Помилка: порушення послідовності seq на кроці %zu [seq = %u]\n", i, items[i].seq);
            return false;
        }
        if (items[i].command == MAV_CMD_NAV_WAYPOINT || items[i].command == MAV_CMD_NAV_TAKEOFF) {
            double lat = degE7_to_deg(items[i].x);
            double lon = degE7_to_deg(items[i].y);
            if (lat < -90.0 || lat > 90.0 || lon < -180.0 || lon > 180.0) {
                printf("Помилка: некоректні географічні координати у seq %zu (lat: %f, lon: %f)\n", i, lat, lon);
                return false;
            }
            if (items[i].z < 2.0f || items[i].z > 5000.0f) {
                printf("Помилка: небезпечна висота z = %.1f м у seq %zu\n", items[i].z, i);
                return false;
            }
        }
        if (items[i].command == MAV_CMD_DO_JUMP) {
            uint16_t target = (uint16_t)items[i].param1;
            if (target >= count || target == i) {
                printf("Помилка: DO_JUMP у seq %zu посилається на неприпустимий цільовий індекс %u\n", i, target);
                return false;
            }
        }
    }
    return true;
}

int main(void) {
    mavlink_mission_item_int_t mission[8];
    double home_lat = 50.4501;
    double home_lon = 30.5234;
    float survey_alt = 60.0f; // Висота польоту 60 м

    double w1_lat, w1_lon, w2_lat, w2_lon, w3_lat, w3_lon, w4_lat, w4_lon;
    add_meter_offset(home_lat, home_lon, 100.0, 0.0, &w1_lat, &w1_lon);
    add_meter_offset(home_lat, home_lon, 100.0, 300.0, &w2_lat, &w2_lon);
    add_meter_offset(home_lat, home_lon, 200.0, 300.0, &w3_lat, &w3_lon);
    add_meter_offset(home_lat, home_lon, 200.0, 0.0, &w4_lat, &w4_lon);

    // Збирання польотного завдання
    mission[0] = make_takeoff(0, home_lat, home_lon, survey_alt);
    mission[1] = make_change_speed(1, 14.0f); // 14 м/с робоча швидкість
    mission[2] = make_camera_trigger(2, 20.0f); // Фото кожні 20 м
    mission[3] = make_waypoint(3, w1_lat, w1_lon, survey_alt, 0.0f, 5.0f, 12.0f);
    mission[4] = make_waypoint(4, w2_lat, w2_lon, survey_alt, 0.0f, 5.0f, 12.0f);
    mission[5] = make_waypoint(5, w3_lat, w3_lon, survey_alt, 0.0f, 5.0f, 12.0f);
    mission[6] = make_waypoint(6, w4_lat, w4_lon, survey_alt, 0.0f, 5.0f, 12.0f);
    mission[7] = make_rtl(7);

    if (validate_mission(mission, 8)) {
        printf("Польотне завдання успішно скомпільовано та верифіковано.\n");
        printf("Всього елементів: 8. Розмір корисних даних у пам'яті: %zu байтів.\n", 8 * sizeof(mavlink_mission_item_int_t));
        for (size_t i = 0; i < 8; ++i) {
            printf("Item %u: CMD=%3u, X=%9d, Y=%9d, Z=%5.1f м, P1=%5.1f, P2=%5.1f\n",
                   mission[i].seq, mission[i].command, mission[i].x, mission[i].y,
                   mission[i].z, mission[i].param1, mission[i].param2);
        }
    }
    return 0;
}
