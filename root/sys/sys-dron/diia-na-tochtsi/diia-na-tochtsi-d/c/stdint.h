#include <stdint.h>
#include <stdbool.h>

// Типи дій корисного навантаження в польотному плані
typedef enum {
    PAYLOAD_ACTION_NONE = 0,
    PAYLOAD_ACTION_TRIGGER_SHUTTER,
    PAYLOAD_ACTION_SET_DISTANCE_TRIGGER,
    PAYLOAD_ACTION_SET_ROI,
    PAYLOAD_ACTION_CLEAR_ROI,
    PAYLOAD_ACTION_RELEASE_CARGO
} payload_action_type_t;

// Параметри команди на точці
typedef struct {
    payload_action_type_t type;
    union {
        struct {
            float distance_interval_m;
        } cam_dist;
        struct {
            double latitude;
            double longitude;
            float altitude_m;
        } roi;
        struct {
            uint16_t release_timeout_ms;
            uint8_t  retry_limit;
        } drop;
    } params;
} mission_payload_cmd_t;

// Стан виконання поточної дії
typedef enum {
    ACTION_STATUS_IDLE = 0,
    ACTION_STATUS_RUNNING,
    ACTION_STATUS_COMPLETED,
    ACTION_STATUS_FAILED
} action_status_t;

// Публічні виклики інтерфейсу
void payload_subsystem_init(void);
action_status_t payload_dispatch_cmd(const mission_payload_cmd_t *cmd);
void payload_subsystem_tick_50hz(void);
