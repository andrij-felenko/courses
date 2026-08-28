#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef enum {
    FSM_STATE_INIT = 0,
    FSM_STATE_CONNECT_SAVED,
    FSM_STATE_PROV_ACTIVE,
    FSM_STATE_VALIDATING,
    FSM_STATE_OPERATIONAL,
    FSM_STATE_PROV_FAILED
} prov_fsm_state_t;

typedef enum {
    FSM_EVT_START,
    FSM_EVT_CREDS_RECEIVED,
    FSM_EVT_STATION_CONNECTED,
    FSM_EVT_STATION_AUTH_FAIL,
    FSM_EVT_STATION_NOT_FOUND,
    FSM_EVT_RETRY_TIMEOUT,
    FSM_EVT_FACTORY_RESET
} prov_fsm_event_t;

typedef struct {
    char ssid[33];
    char password[65];
} fsm_credentials_t;

typedef struct {
    prov_fsm_state_t state;
    uint8_t retry_count;
    fsm_credentials_t current_creds;
    fsm_credentials_t pending_creds;
} prov_fsm_context_t;

/* Зовнішні системні функції платформи */
extern bool nvs_read_credentials(fsm_credentials_t *creds);
extern bool nvs_write_credentials(const fsm_credentials_t *creds);
extern void nvs_erase_credentials(void);
extern void wifi_start_station(const char *ssid, const char *pass);
extern void ble_prov_start_service(void);
extern void ble_prov_stop_service(void);
extern void ble_prov_send_status(int error_code);

void prov_fsm_init(prov_fsm_context_t *ctx) {
    memset(ctx, 0, sizeof(prov_fsm_context_t));
    ctx->state = FSM_STATE_INIT;
}

void prov_fsm_dispatch(prov_fsm_context_t *ctx, prov_fsm_event_t event, const void *event_data) {
    if (event == FSM_EVT_FACTORY_RESET) {
        nvs_erase_credentials();
        ble_prov_start_service();
        ctx->state = FSM_STATE_PROV_ACTIVE;
        return;
    }

    switch (ctx->state) {
    case FSM_STATE_INIT:
        if (event == FSM_EVT_START) {
            if (nvs_read_credentials(&ctx->current_creds)) {
                wifi_start_station(ctx->current_creds.ssid, ctx->current_creds.password);
                ctx->retry_count = 0;
                ctx->state = FSM_STATE_CONNECT_SAVED;
            } else {
                ble_prov_start_service();
                ctx->state = FSM_STATE_PROV_ACTIVE;
            }
        }
        break;

    case FSM_STATE_CONNECT_SAVED:
        if (event == FSM_EVT_STATION_CONNECTED) {
            ctx->state = FSM_STATE_OPERATIONAL;
        } else if (event == FSM_EVT_STATION_AUTH_FAIL || event == FSM_EVT_STATION_NOT_FOUND) {
            if (++ctx->retry_count >= 3) {
                ble_prov_start_service();
                ctx->state = FSM_STATE_PROV_ACTIVE;
            } else {
                wifi_start_station(ctx->current_creds.ssid, ctx->current_creds.password);
            }
        }
        break;

    case FSM_STATE_PROV_ACTIVE:
        if (event == FSM_EVT_CREDS_RECEIVED && event_data) {
            memcpy(&ctx->pending_creds, event_data, sizeof(fsm_credentials_t));
            wifi_start_station(ctx->pending_creds.ssid, ctx->pending_creds.password);
            ctx->state = FSM_STATE_VALIDATING;
        }
        break;

    case FSM_STATE_VALIDATING:
        if (event == FSM_EVT_STATION_CONNECTED) {
            memcpy(&ctx->current_creds, &ctx->pending_creds, sizeof(fsm_credentials_t));
            nvs_write_credentials(&ctx->current_creds);
            ble_prov_send_status(0); // Success
            ble_prov_stop_service();
            ctx->state = FSM_STATE_OPERATIONAL;
        } else if (event == FSM_EVT_STATION_AUTH_FAIL) {
            ble_prov_send_status(1); // Auth failed
            ctx->state = FSM_STATE_PROV_FAILED;
        } else if (event == FSM_EVT_STATION_NOT_FOUND) {
            ble_prov_send_status(2); // AP not found
            ctx->state = FSM_STATE_PROV_FAILED;
        }
        break;

    case FSM_STATE_PROV_FAILED:
        if (event == FSM_EVT_CREDS_RECEIVED && event_data) {
            memcpy(&ctx->pending_creds, event_data, sizeof(fsm_credentials_t));
            wifi_start_station(ctx->pending_creds.ssid, ctx->pending_creds.password);
            ctx->state = FSM_STATE_VALIDATING;
        } else if (event == FSM_EVT_RETRY_TIMEOUT) {
            ctx->state = FSM_STATE_PROV_ACTIVE;
        }
        break;

    case FSM_STATE_OPERATIONAL:
        /* Нормальна робота пристрою */
        break;
    }
}
