#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define MAVLINK_MSG_ID_MISSION_ITEM_INT 73
#define MISSION_ITEM_INT_PAYLOAD_LEN    38

typedef struct __attribute__((packed)) {
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

typedef enum {
    RESULT_ACCEPTED = 0,
    RESULT_ERROR = 1,
    RESULT_UNSUPPORTED_FRAME = 2,
    RESULT_UNSUPPORTED_CMD = 3,
    RESULT_INVALID_PARAM1 = 6,
    RESULT_INVALID_PARAM2 = 7,
    RESULT_INVALID_COORDS = 10,
    RESULT_INVALID_SEQ = 13
} mission_validation_result_t;

// Валідація дескриптора точки перед записом у пам'ять
mission_validation_result_t validate_mission_item(const mavlink_mission_item_int_t *item, uint16_t expected_seq) {
    if (item->seq != expected_seq) {
        return RESULT_INVALID_SEQ;
    }
    
    // Перевірка допустимості фрейму
    if (item->frame != 0 && item->frame != 3 && item->frame != 6 && item->frame != 10 && item->frame != 11) {
        return RESULT_UNSUPPORTED_FRAME;
    }
    
    // Перевірка геометричних параметрів радіуса прийняття та затримки
    if (item->command == 16) { // NAV_WAYPOINT
        if (item->param1 < 0.0f) {
            return RESULT_INVALID_PARAM1;
        }
        if (item->param2 < 0.0f) {
            return RESULT_INVALID_PARAM2;
        }
    }

    // Перевірка географічних меж для глобальних координат (широта [-90..+90], довгота [-180..+180])
    if (item->frame == 0 || item->frame == 3 || item->frame == 6 || item->frame == 10 || item->frame == 11) {
        if (item->x < -900000000 || item->x > 900000000) {
            return RESULT_INVALID_COORDS;
        }
        if (item->y < -1800000000 || item->y > 1800000000) {
            return RESULT_INVALID_COORDS;
        }
    }
    
    if (isnan(item->z) || isnan(item->param1) || isnan(item->param2)) {
        return RESULT_INVALID_COORDS;
    }
    
    return RESULT_ACCEPTED;
}
