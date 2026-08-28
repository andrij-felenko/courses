#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define IEEE80211_ELEMID_NEIGHBOR_REPORT  0x34
#define IEEE80211_ELEMID_MOBILITY_DOMAIN  0x36
#define IEEE80211_ELEMID_FAST_TRANSITION  0x37

#define WNM_CATEGORY_CODE                 0x0A
#define WNM_ACTION_BTM_REQ                0x07
#define WNM_ACTION_BTM_RESP               0x08

#pragma pack(push, 1)

typedef struct {
    uint8_t  element_id;
    uint8_t  length;
    uint8_t  bssid[6];
    uint32_t bssid_info;
    uint8_t  reg_class;
    uint8_t  channel_number;
    uint8_t  phy_type;
} neighbor_report_fixed_t;

typedef struct {
    uint8_t  element_id;
    uint8_t  length;
    uint16_t mdid;
    uint8_t  ft_capability;
} mobility_domain_ie_t;

typedef struct {
    uint8_t  element_id;
    uint8_t  length;
    uint16_t mic_control;
    uint8_t  mic[16];
    uint8_t  anonce[32];
    uint8_t  snonce[32];
} fast_transition_ie_t;

typedef struct {
    uint8_t  category;        /* 0x0A - WNM */
    uint8_t  action;          /* 0x07 - BTM Request */
    uint8_t  dialog_token;
    uint8_t  request_mode;
    uint16_t disassoc_timer;  /* в одиницях TBTT */
    uint8_t  validity_interval;
} btm_request_fixed_t;

#pragma pack(pop)

bool parse_mobility_domain(const uint8_t *payload, uint16_t len, uint16_t *out_mdid, bool *out_over_ds) {
    if (!payload || len < sizeof(mobility_domain_ie_t) || !out_mdid || !out_over_ds) {
        return false;
    }
    const mobility_domain_ie_t *mde = (const mobility_domain_ie_t *)payload;
    if (mde->element_id != IEEE80211_ELEMID_MOBILITY_DOMAIN || mde->length < 3) {
        return false;
    }
    *out_mdid = mde->mdid;
    *out_over_ds = (mde->ft_capability & 0x01) != 0;
    return true;
}

bool is_neighbor_ft_capable(const uint8_t *payload, uint16_t len, uint8_t *out_channel) {
    if (!payload || len < sizeof(neighbor_report_fixed_t) || !out_channel) {
        return false;
    }
    const neighbor_report_fixed_t *rep = (const neighbor_report_fixed_t *)payload;
    if (rep->element_id != IEEE80211_ELEMID_NEIGHBOR_REPORT || rep->length < 13) {
        return false;
    }
    *out_channel = rep->channel_number;
    /* Біт 10 у BSSID Information вказує на підтримку 802.11r FT */
    return (rep->bssid_info & (1U << 10)) != 0;
}
