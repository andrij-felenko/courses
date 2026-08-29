#define _POSIX_C_SOURCE 200809L

#include "ble_scan.h"

#include <errno.h>
#include <poll.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

/* Константи ABI ядра. Оголошуємо їх тут, щоб не тягнути в шлюз увесь bluez:
 * значення зафіксовані інтерфейсом ядра й не змінюються. */
#define BT_AF               31   /* AF_BLUETOOTH */
#define BT_PROTO_HCI        1
#define HCI_CHANNEL_RAW     0
#define SOL_HCI_LEVEL       0
#define HCI_FILTER_OPT      2

#define HCI_COMMAND_PKT     0x01
#define HCI_EVENT_PKT       0x04

#define EVT_CMD_COMPLETE    0x0E
#define EVT_LE_META         0x3E
#define LE_ADVERTISING_REPORT 0x02

/* OGF 0x08 (LE Controller) → opcode = (OGF << 10) | OCF */
#define OCF_LE_SET_SCAN_PARAMS 0x200B
#define OCF_LE_SET_SCAN_ENABLE 0x200C

/* Тип структури рекламних даних: Service Data — 16-бітний UUID (Core Spec). */
#define AD_TYPE_SERVICE_DATA_16 0x16
/* Environmental Sensing Service — під цим UUID наш давач кладе свій блок. */
#define UUID_ENV_SENSING        0x181A
/* Розкладка блоку давача: версія формату, int16 температури в сотих градуса
 * (молодшим байтом уперед), заряд у відсотках. */
#define SENSOR_FORMAT_V1        0x01

struct sockaddr_hci {
    unsigned short hci_family;
    unsigned short hci_dev;
    unsigned short hci_channel;
};

struct hci_filter {
    uint32_t type_mask;
    uint32_t event_mask[2];
    uint16_t opcode;
};

struct ble_scanner {
    int fd;
};

static bool hci_send_command(int fd, uint16_t opcode, const uint8_t *params, uint8_t plen)
{
    uint8_t pkt[4 + 255];
    pkt[0] = HCI_COMMAND_PKT;
    pkt[1] = (uint8_t)(opcode & 0xFF);
    pkt[2] = (uint8_t)(opcode >> 8);
    pkt[3] = plen;
    if (plen)
        memcpy(pkt + 4, params, plen);

    ssize_t n = write(fd, pkt, (size_t)plen + 4);
    if (n != (ssize_t)plen + 4)
        return false;

    /* Чекаємо на Command Complete саме нашої команди: без підтвердження ми не
     * знаємо, чи контролер узагалі почав сканувати. */
    for (int attempt = 0; attempt < 32; attempt++) {
        struct pollfd pfd = { fd, POLLIN, 0 };
        int pr = poll(&pfd, 1, 1000);
        if (pr <= 0)
            return false;

        uint8_t buf[260];
        ssize_t got = read(fd, buf, sizeof(buf));
        if (got < 7)
            continue;
        if (buf[0] != HCI_EVENT_PKT || buf[1] != EVT_CMD_COMPLETE)
            continue;

        uint16_t answered = (uint16_t)(buf[4] | ((uint16_t)buf[5] << 8));
        if (answered != opcode)
            continue;
        return buf[6] == 0x00;   /* нульовий статус — команда прийнята */
    }
    return false;
}

static bool set_scan_enable(int fd, bool enable)
{
    uint8_t params[2] = { enable ? 0x01 : 0x00, 0x01 };  /* другий байт — фільтр дублів */
    return hci_send_command(fd, OCF_LE_SET_SCAN_ENABLE, params, sizeof(params));
}

ble_scanner_t *ble_open(int hci_index)
{
    int fd = socket(BT_AF, SOCK_RAW, BT_PROTO_HCI);
    if (fd < 0)
        return NULL;

    struct sockaddr_hci addr;
    memset(&addr, 0, sizeof(addr));
    addr.hci_family = BT_AF;
    addr.hci_dev = (unsigned short)hci_index;
    addr.hci_channel = HCI_CHANNEL_RAW;
    if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        close(fd);
        return NULL;
    }

    /* Пропускаємо в сокет усі події й відсіюємо потрібні самі: розбір усе одно
     * робиться в одному місці, а фільтр ядра тут нічого не заощадив би. */
    struct hci_filter filter;
    memset(&filter, 0, sizeof(filter));
    filter.type_mask = 1u << HCI_EVENT_PKT;
    filter.event_mask[0] = 0xFFFFFFFFu;
    filter.event_mask[1] = 0xFFFFFFFFu;
    if (setsockopt(fd, SOL_HCI_LEVEL, HCI_FILTER_OPT, &filter, sizeof(filter)) < 0) {
        close(fd);
        return NULL;
    }

    /* Скидаємо можливе попереднє сканування, інакше зміна параметрів
     * відхиляється з Command Disallowed. */
    set_scan_enable(fd, false);

    uint8_t scan_params[7] = {
        0x00,          /* пасивне сканування: SCAN_REQ не шлемо, ефір не гріємо */
        0xA0, 0x00,    /* інтервал 0x00A0 × 0.625 мс = 100 мс */
        0xA0, 0x00,    /* вікно дорівнює інтервалу — слухаємо безперервно */
        0x00,          /* власна адреса — публічна */
        0x00           /* приймати рекламу від усіх, білого списку немає */
    };
    if (!hci_send_command(fd, OCF_LE_SET_SCAN_PARAMS, scan_params, sizeof(scan_params)) ||
        !set_scan_enable(fd, true)) {
        close(fd);
        return NULL;
    }

    ble_scanner_t *s = calloc(1, sizeof(*s));
    if (!s) {
        set_scan_enable(fd, false);
        close(fd);
        return NULL;
    }
    s->fd = fd;
    return s;
}

void ble_close(ble_scanner_t *s)
{
    if (!s)
        return;
    set_scan_enable(s->fd, false);   /* лишити радіо ввімкненим — гріти акумулятор шлюза */
    close(s->fd);
    free(s);
}

/* Розбір поля рекламних даних: послідовність структур «довжина, тип, вміст». */
static bool parse_sensor_payload(const uint8_t *ad, size_t ad_len, ble_sample_t *out)
{
    size_t i = 0;
    while (i < ad_len) {
        uint8_t len = ad[i];
        if (len == 0)
            break;                       /* нульова довжина — кінець корисних даних */
        if (i + 1 + len > ad_len)
            return false;                /* кадр обрізаний: довіряти йому не можна */

        uint8_t type = ad[i + 1];
        const uint8_t *body = &ad[i + 2];
        size_t body_len = (size_t)len - 1;

        if (type == AD_TYPE_SERVICE_DATA_16 && body_len >= 6) {
            uint16_t uuid = (uint16_t)(body[0] | ((uint16_t)body[1] << 8));
            if (uuid == UUID_ENV_SENSING && body[2] == SENSOR_FORMAT_V1) {
                int16_t centi = (int16_t)(body[3] | ((uint16_t)body[4] << 8));
                out->temperature_c = centi / 100.0f;
                out->battery_pct = body[5];
                return true;
            }
        }
        i += 1 + len;
    }
    return false;
}

int ble_next_sample(ble_scanner_t *s, ble_sample_t *out, int timeout_ms)
{
    struct pollfd pfd = { s->fd, POLLIN, 0 };
    int pr = poll(&pfd, 1, timeout_ms);
    if (pr == 0)
        return 0;
    if (pr < 0)
        return (errno == EINTR) ? 0 : -1;

    uint8_t buf[260];
    ssize_t n = read(s->fd, buf, sizeof(buf));
    if (n < 0)
        return (errno == EINTR || errno == EAGAIN) ? 0 : -1;
    if (n == 0)
        return -1;

    /* HCI-подія: [тип пакета][код події][довжина][параметри] */
    if (n < 5 || buf[0] != HCI_EVENT_PKT || buf[1] != EVT_LE_META)
        return 0;
    if (buf[3] != LE_ADVERTISING_REPORT)
        return 0;

    uint8_t num_reports = buf[4];
    size_t off = 5;
    for (uint8_t r = 0; r < num_reports; r++) {
        /* Звіт: тип події(1), тип адреси(1), адреса(6), довжина даних(1),
         * дані(len), RSSI(1). */
        if (off + 9 > (size_t)n)
            return 0;
        const uint8_t *addr = &buf[off + 2];
        uint8_t data_len = buf[off + 8];
        if (off + 9 + data_len + 1 > (size_t)n)
            return 0;

        ble_sample_t sample;
        memset(&sample, 0, sizeof(sample));
        if (parse_sensor_payload(&buf[off + 9], data_len, &sample)) {
            memcpy(sample.addr, addr, 6);
            sample.rssi_dbm = (int8_t)buf[off + 9 + data_len];
            *out = sample;
            return 1;
        }
        off += 9 + (size_t)data_len + 1;
    }
    return 0;
}
