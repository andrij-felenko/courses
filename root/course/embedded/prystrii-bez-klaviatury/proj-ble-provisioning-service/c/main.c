/*
 * Диспетчер GATT-сервісу провізіонування: звʼязує події BLE-стека
 * з криптографічною сесією, а результат Wi-Fi — зі сповіщеннями клієнту.
 */
#include "att_reassembly.h"
#include "prov_crypto.h"
#include "prov_platform.h"
#include "prov_session.h"

#include <string.h>

#define PROV_UUID_SERVICE  0xFF50
#define PROV_UUID_SESSION  0xFF51
#define PROV_UUID_CONFIG   0xFF52

/* Скільки тримати радіо після успіху, щоб сповіщення встигло вийти в ефір. */
#define PROV_BLE_LINGER_MS 2000

static prov_session_t     g_session;
static att_reasm_t        g_reasm;
static prov_credentials_t g_pending;         /* чекають на підтвердження від Wi-Fi */
static uint8_t            g_session_resp[PROV_SESSION_RESP_SIZE];
static size_t             g_session_resp_len;
static uint16_t           g_mtu = ATT_MTU_DEFAULT;
static bool               g_provisioned;

void prov_service_start(void)
{
    const uint8_t *pop = NULL;
    size_t pop_len = plat_pop_secret(&pop);

    prov_session_init(&g_session, pop, pop_len);
    att_reasm_cancel(&g_reasm);
    memset(&g_pending, 0, sizeof(g_pending));
    g_session_resp_len = 0;
    g_mtu = ATT_MTU_DEFAULT;
    g_provisioned = false;

    plat_ble_advertise();
}

/* Сповіщення на prov-config: [статус 1][IPv4 4] — влазить навіть у базові 20 байтів. */
static void notify_status(prov_status_t status, uint32_t ipv4, bool with_ip)
{
    uint8_t frame[5];
    size_t len = 0;

    frame[len++] = (uint8_t)status;
    if (with_ip) {
        frame[len++] = (uint8_t)(ipv4 >> 24);
        frame[len++] = (uint8_t)(ipv4 >> 16);
        frame[len++] = (uint8_t)(ipv4 >> 8);
        frame[len++] = (uint8_t)(ipv4);
    }
    if (len > att_mtu_payload(g_mtu)) {
        len = att_mtu_payload(g_mtu);
    }
    plat_ble_notify(PROV_UUID_CONFIG, frame, len);
}

static void ble_linger_expired(void)
{
    prov_session_reset(&g_session);
    att_reasm_cancel(&g_reasm);
    plat_ble_shutdown();            /* радіо вимкнене, RAM стека — застосунку */
}

static void handle_session_write(const uint8_t *data, size_t len)
{
    prov_status_t st = prov_session_handshake(&g_session, data, len,
                                              g_session_resp, &g_session_resp_len);
    if (st != PROV_STATUS_SUCCESS) {
        prov_secure_wipe(g_session_resp, sizeof(g_session_resp));
        g_session_resp_len = 0;
        notify_status(st, 0, false);
    }
    /* За успіху клієнт забирає відповідь читанням prov-session. */
}

static void handle_config_write(const uint8_t *data, size_t len)
{
    prov_credentials_t creds;
    prov_status_t st = prov_session_config(&g_session, data, len, &creds);
    if (st != PROV_STATUS_SUCCESS) {
        notify_status(st, 0, false);
        return;
    }

    /* У NVS кладемо не зараз, а лише коли точка доступу справді пустила. */
    memcpy(&g_pending, &creds, sizeof(g_pending));
    prov_secure_wipe(&creds, sizeof(creds));
    plat_wifi_connect(g_pending.ssid, g_pending.password);
}

static void dispatch_write(uint16_t char_uuid, const uint8_t *data, size_t len)
{
    switch (char_uuid) {
    case PROV_UUID_SESSION: handle_session_write(data, len); break;
    case PROV_UUID_CONFIG:  handle_config_write(data, len);  break;
    default: break;         /* чужий атрибут — не наша характеристика */
    }
}

void prov_on_connect(void)
{
    g_mtu = ATT_MTU_DEFAULT;        /* до узгодження живемо на базовому кадрі */
    att_reasm_cancel(&g_reasm);
}

uint16_t prov_on_mtu_exchange(uint16_t client_mtu)
{
    g_mtu = att_mtu_negotiate(client_mtu);
    return g_mtu;                   /* стек відповість цим значенням клієнту */
}

void prov_on_gatt_write(uint16_t char_uuid, const uint8_t *data, size_t len)
{
    dispatch_write(char_uuid, data, len);
}

uint16_t prov_on_gatt_read(uint16_t char_uuid, uint8_t *out, uint16_t max_len)
{
    if (char_uuid != PROV_UUID_SESSION || g_session_resp_len == 0) {
        return 0;
    }
    uint16_t len = (uint16_t)g_session_resp_len;
    if (len > max_len) {
        len = max_len;              /* довге читання клієнт добере за зміщенням */
    }
    memcpy(out, g_session_resp, len);
    return len;
}

uint8_t prov_on_prepare_write(uint16_t char_uuid, uint16_t offset,
                              const uint8_t *value, size_t len)
{
    return att_reasm_prepare(&g_reasm, char_uuid, offset, value, len);
}

uint8_t prov_on_execute_write(bool commit)
{
    uint16_t uuid = 0;
    const uint8_t *value = NULL;
    size_t len = 0;

    uint8_t err = att_reasm_execute(&g_reasm, commit, &uuid, &value, &len);
    if (err == ATT_ERR_NONE && len > 0) {
        dispatch_write(uuid, value, len);
    }
    att_reasm_cancel(&g_reasm);     /* зібране значення вже спожите */
    return err;
}

void prov_on_wifi_event(plat_wifi_event_t event, uint32_t ipv4)
{
    switch (event) {
    case PLAT_WIFI_CONNECTED:
        if (!plat_nvs_store_credentials(g_pending.ssid, g_pending.password)) {
            notify_status(PROV_STATUS_STORAGE_FAIL, 0, false);
            break;
        }
        notify_status(PROV_STATUS_SUCCESS, ipv4, true);
        prov_secure_wipe(&g_pending, sizeof(g_pending));
        g_provisioned = true;
        plat_timer_once(PROV_BLE_LINGER_MS, ble_linger_expired);
        break;

    case PLAT_WIFI_AUTH_FAILED:
        /* Сесію тримаємо відкритою: клієнт виправить пароль без нового пошуку. */
        plat_wifi_stop();
        prov_secure_wipe(&g_pending, sizeof(g_pending));
        notify_status(PROV_STATUS_AUTH_FAIL, 0, false);
        break;

    case PLAT_WIFI_NO_AP:
    case PLAT_WIFI_TIMEOUT:
    default:
        plat_wifi_stop();
        prov_secure_wipe(&g_pending, sizeof(g_pending));
        notify_status(PROV_STATUS_STATION_TIMEOUT, 0, false);
        break;
    }
}

void prov_on_disconnect(uint8_t hci_reason)
{
    (void)hci_reason;               /* 0x08 — таймаут нагляду; для нас усі розриви однакові */

    att_reasm_cancel(&g_reasm);
    prov_secure_wipe(g_session_resp, sizeof(g_session_resp));
    g_session_resp_len = 0;
    prov_secure_wipe(&g_pending, sizeof(g_pending));
    prov_session_reset(&g_session);
    g_mtu = ATT_MTU_DEFAULT;

    if (g_provisioned) {
        plat_ble_shutdown();
    } else {
        plat_wifi_stop();           /* незавершена перевірка пароля нікому не потрібна */
        plat_ble_advertise();       /* назад у рекламу — сесія не зависає напіввідкритою */
    }
}
