#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_COMMAND_LEN 64
#define MAX_RESPONSE_LEN 128

typedef enum {
    DEVICE_CMD_GET_STATUS = 0x01,
    DEVICE_CMD_SET_RELAY  = 0x02,
    DEVICE_CMD_GET_TELEMETRY = 0x03,
    DEVICE_CMD_INVALID    = 0xFF
} device_cmd_type_t;

typedef struct {
    bool relay_state;
    int16_t temperature_c_x10;
    uint32_t uptime_sec;
} device_core_state_t;

static device_core_state_t g_device_state = {
    .relay_state = false,
    .temperature_c_x10 = 225, /* 22.5 C */
    .uptime_sec = 0
};

/* Апаратна зміна стану виконавчого механізму */
extern void hal_gpio_set_relay(bool enable);

/* Обробка локальної команди (з HTTP, MQTT або BLE) */
bool local_dispatcher_handle_command(const char *cmd_json, char *resp_json, size_t max_resp) {
    if (strstr(cmd_json, "\"cmd\":\"get_status\"") != NULL) {
        snprintf(resp_json, max_resp, 
                 "{\"status\":\"ok\",\"relay\":%s,\"temp\":%.1f,\"uptime\":%lu}",
                 g_device_state.relay_state ? "true" : "false",
                 g_device_state.temperature_c_x10 / 10.0,
                 (unsigned long)g_device_state.uptime_sec);
        return true;
    }
    
    if (strstr(cmd_json, "\"cmd\":\"set_relay\"") != NULL) {
        if (strstr(cmd_json, "\"state\":true") != NULL) {
            g_device_state.relay_state = true;
            hal_gpio_set_relay(true);
        } else if (strstr(cmd_json, "\"state\":false") != NULL) {
            g_device_state.relay_state = false;
            hal_gpio_set_relay(false);
        } else {
            snprintf(resp_json, max_resp, "{\"status\":\"error\",\"msg\":\"invalid_state\"}");
            return false;
        }
        
        snprintf(resp_json, max_resp, "{\"status\":\"ok\",\"relay\":%s}",
                 g_device_state.relay_state ? "true" : "false");
        return true;
    }

    snprintf(resp_json, max_resp, "{\"status\":\"error\",\"msg\":\"unknown_command\"}");
    return false;
}
