// event_types.h
#ifndef EVENT_TYPES_H
#define EVENT_TYPES_H

#include <stdint.h>

typedef enum {
    EVT_ID_NONE = 0,
    EVT_ID_TICK_100MS,
    EVT_ID_BUTTON_CLICK,
    EVT_ID_SENSOR_DATA_READY,
    EVT_ID_ALARM_OVERTEMP,
    EVT_ID_COMMS_PACKET_RX
} event_id_t;

typedef struct {
    event_id_t id;
    uint32_t timestamp_ms;
    union {
        uint8_t button_pin;
        struct {
            float temp_c;
            float pressure_kpa;
        } sensor_payload;
        struct {
            uint16_t len;
            const uint8_t* p_data;
        } rx_packet;
    } data;
} sys_event_t;

#endif // EVENT_TYPES_H
