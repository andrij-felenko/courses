#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_SSID_LEN        32
#define MAX_PASSPHRASE_LEN  64
#define MAX_ENDPOINT_LEN    128
#define CLAIM_TOKEN_LEN     32
#define POP_PIN_LEN         8
#define CONFIG_TIMEOUT_SEC  300

typedef enum {
    ONBOARD_STATUS_OK = 0,
    ONBOARD_ERR_INVALID_STATE,
    ONBOARD_ERR_AUTH_FAILED,
    ONBOARD_ERR_NET_TIMEOUT,
    ONBOARD_ERR_CLOUD_REJECTED,
    ONBOARD_ERR_STORAGE_FAULT
} onboard_result_t;

typedef enum {
    ONBOARD_ST_FACTORY_RESET = 0,
    ONBOARD_ST_CHANNEL_LISTENING,
    ONBOARD_ST_AUTHENTICATING,
    ONBOARD_ST_CONFIG_RECEIVED,
    ONBOARD_ST_NETWORK_CONNECTING,
    ONBOARD_ST_CLOUD_ENROLLING,
    ONBOARD_ST_CLAIMED_LOCKED
} onboard_fsm_state_t;

typedef struct {
    char ssid[MAX_SSID_LEN + 1];
    char passphrase[MAX_PASSPHRASE_LEN + 1];
    char cloud_endpoint[MAX_ENDPOINT_LEN + 1];
    uint8_t claim_token[CLAIM_TOKEN_LEN];
    uint16_t cloud_port;
    bool is_valid;
} network_provision_payload_t;

typedef struct {
    onboard_fsm_state_t current_state;
    network_provision_payload_t pending_config;
    uint32_t session_timer_sec;
    uint8_t failed_auth_attempts;
    char factory_pop_pin[POP_PIN_LEN + 1];
    bool is_channel_locked;
} onboard_controller_t;

/* Заглушки драйверів апаратного рівня */
extern void hw_radio_start_advertising(void);
extern void hw_radio_stop_advertising(void);
extern bool hw_wifi_connect_station(const char *ssid, const char *pass);
extern bool hw_cloud_request_ldevid(const char *endpoint, uint16_t port, const uint8_t *token);
extern bool hw_secure_storage_save_ldevid(void);
extern bool hw_secure_storage_clear(void);

void onboard_controller_init(onboard_controller_t *ctrl, const char *factory_pin) {
    if (!ctrl || !factory_pin) return;
    memset(ctrl, 0, sizeof(onboard_controller_t));
    ctrl->current_state = ONBOARD_ST_FACTORY_RESET;
    strncpy(ctrl->factory_pop_pin, factory_pin, POP_PIN_LEN);
    ctrl->is_channel_locked = false;
}

onboard_result_t onboard_start_listening(onboard_controller_t *ctrl) {
    if (ctrl->is_channel_locked) {
        return ONBOARD_ERR_INVALID_STATE;
    }
    ctrl->current_state = ONBOARD_ST_CHANNEL_LISTENING;
    ctrl->session_timer_sec = 0;
    ctrl->failed_auth_attempts = 0;
    hw_radio_start_advertising();
    return ONBOARD_STATUS_OK;
}

onboard_result_t onboard_verify_pop(onboard_controller_t *ctrl, const char *provided_pin) {
    if (ctrl->current_state != ONBOARD_ST_CHANNEL_LISTENING) {
        return ONBOARD_ERR_INVALID_STATE;
    }
    
    if (ctrl->failed_auth_attempts >= 3) {
        /* Захист від перебору: блокування до таймауту сесії */
        return ONBOARD_ERR_AUTH_FAILED;
    }

    if (strncmp(ctrl->factory_pop_pin, provided_pin, POP_PIN_LEN) == 0) {
        ctrl->current_state = ONBOARD_ST_AUTHENTICATING;
        ctrl->failed_auth_attempts = 0;
        return ONBOARD_STATUS_OK;
    } else {
        ctrl->failed_auth_attempts++;
        return ONBOARD_ERR_AUTH_FAILED;
    }
}

onboard_result_t onboard_apply_credentials(onboard_controller_t *ctrl, const network_provision_payload_t *cfg) {
    if (ctrl->current_state != ONBOARD_ST_AUTHENTICATING || !cfg) {
        return ONBOARD_ERR_INVALID_STATE;
    }

    memcpy(&ctrl->pending_config, cfg, sizeof(network_provision_payload_t));
    ctrl->pending_config.is_valid = true;
    ctrl->current_state = ONBOARD_ST_CONFIG_RECEIVED;

    /* Спроба асоціації з точкою доступу */
    ctrl->current_state = ONBOARD_ST_NETWORK_CONNECTING;
    if (!hw_wifi_connect_station(ctrl->pending_config.ssid, ctrl->pending_config.passphrase)) {
        ctrl->current_state = ONBOARD_ST_CHANNEL_LISTENING;
        return ONBOARD_ERR_NET_TIMEOUT;
    }

    /* Підключення до хмари для отримання робочого LDevID */
    ctrl->current_state = ONBOARD_ST_CLOUD_ENROLLING;
    if (!hw_cloud_request_ldevid(ctrl->pending_config.cloud_endpoint,
                                 ctrl->pending_config.cloud_port,
                                 ctrl->pending_config.claim_token)) {
        ctrl->current_state = ONBOARD_ST_CHANNEL_LISTENING;
        return ONBOARD_ERR_CLOUD_REJECTED;
    }

    /* Збереження сертифіката і блокування конфігураційного порту */
    if (!hw_secure_storage_save_ldevid()) {
        return ONBOARD_ERR_STORAGE_FAULT;
    }

    hw_radio_stop_advertising();
    ctrl->is_channel_locked = true;
    ctrl->current_state = ONBOARD_ST_CLAIMED_LOCKED;
    return ONBOARD_STATUS_OK;
}

void onboard_timer_tick_1hz(onboard_controller_t *ctrl) {
    if (ctrl->current_state == ONBOARD_ST_CHANNEL_LISTENING ||
        ctrl->current_state == ONBOARD_ST_AUTHENTICATING) {
        ctrl->session_timer_sec++;
        if (ctrl->session_timer_sec >= CONFIG_TIMEOUT_SEC) {
            /* Таймаут бездіяльності: вимикаємо радіо для економії живлення та безпеки */
            hw_radio_stop_advertising();
            ctrl->current_state = ONBOARD_ST_FACTORY_RESET;
        }
    }
}
