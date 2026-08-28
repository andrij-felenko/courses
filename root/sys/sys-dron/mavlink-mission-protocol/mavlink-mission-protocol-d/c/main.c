#include <mavlink.h>
#include <stdio.h>
#include <string.h>

// Підготовка списку з 3 пунктів для автопілота ArduPilot
void prepare_mission_c(mavlink_mission_item_int_t* items) {
    // Елемент 0: Home Position (для ArduPilot)
    memset(&items[0], 0, sizeof(items[0]));
    items[0].seq = 0;
    items[0].command = MAV_CMD_NAV_WAYPOINT;
    items[0].frame = MAV_FRAME_GLOBAL_INT;
    items[0].x = (int32_t)(50.4501 * 1e7); // 50.4501 град широти
    items[0].y = (int32_t)(30.5234 * 1e7); // 30.5234 град довготи
    items[0].z = 0.0f;                     // Висота над землею

    // Елемент 1: Зліт на висоту 15 метрів (Takeoff)
    memset(&items[1], 0, sizeof(items[1]));
    items[1].seq = 1;
    items[1].command = MAV_CMD_NAV_TAKEOFF;
    items[1].frame = MAV_FRAME_GLOBAL_RELATIVE_ALT_INT;
    items[1].param7 = 15.0f;               // Цільова висота зльоту
    items[1].x = (int32_t)(50.4501 * 1e7);
    items[1].y = (int32_t)(30.5234 * 1e7);
    items[1].z = 15.0f;
    items[1].autocontinue = 1;

    // Елемент 2: Політ до навігаційної точки на відстані 500 м
    memset(&items[2], 0, sizeof(items[2]));
    items[2].seq = 2;
    items[2].command = MAV_CMD_NAV_WAYPOINT;
    items[2].frame = MAV_FRAME_GLOBAL_RELATIVE_ALT_INT;
    items[2].param2 = 3.0f;                // Радіус прийняття точки (3 метри)
    items[2].x = (int32_t)(50.4545 * 1e7);
    items[2].y = (int32_t)(30.5290 * 1e7);
    items[2].z = 25.0f;                    // Висота польоту 25 м
    items[2].autocontinue = 1;
}

// Відправка ініціалізуючого повідомлення MISSION_COUNT
void start_mission_upload_c(uint8_t sysid, uint8_t compid, uint8_t target_sys, uint16_t count) {
    mavlink_message_t msg;
    mavlink_mission_count_t mc;
    mc.target_system = target_sys;
    mc.target_component = MAV_COMP_ID_AUTOPILOT1;
    mc.count = count;
    mc.mission_type = MAV_MISSION_TYPE_MISSION;

    mavlink_msg_mission_count_encode(sysid, compid, &msg, &mc);
    
    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    uint16_t len = mavlink_msg_to_send_buffer(buf, &msg);
    // serial_write(buf, len) - відправка байтів у радіоканал
}
