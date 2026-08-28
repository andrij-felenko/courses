#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <net/if.h>
#include <netlink/netlink.h>
#include <netlink/genl/genl.h>
#include <netlink/genl/ctrl.h>
#include <linux/nl80211.h>

/* Структура для збереження парсингу відповіді ядра */
typedef struct {
    int bss_color;
    int has_he_support;
    int max_streams;
    uint32_t frequency_mhz;
} wifi6_info_t;

/* Callback-функція обробки відповідей Netlink */
static int parse_nl80211_he_cb(struct nl_msg *msg, void *arg) {
    wifi6_info_t *info = (wifi6_info_t *)arg;
    struct nlmsghdr *nlh = nlmsg_hdr(msg);
    struct genlmsghdr *gnlh = nlmsg_data(nlh);
    struct nlattr *tb[NL80211_ATTR_MAX + 1];

    nla_parse(tb, NL80211_ATTR_MAX, genlmsg_attrdata(gnlh, 0),
              genlmsg_attrlen(gnlh, 0), NULL);

    if (tb[NL80211_ATTR_BSS_COLOR]) {
        info->bss_color = nla_get_u8(tb[NL80211_ATTR_BSS_COLOR]);
    }

    if (tb[NL80211_ATTR_HE_CAPABILITY]) {
        info->has_he_support = 1;
    }

    if (tb[NL80211_ATTR_WIPHY_FREQ]) {
        info->frequency_mhz = nla_get_u32(tb[NL80211_ATTR_WIPHY_FREQ]);
    }

    return NL_SKIP;
}

int query_wifi6_status(const char *ifname, wifi6_info_t *out_info) {
    struct nl_sock *sock = NULL;
    struct nl_msg *msg = NULL;
    int family_id, err = 0;

    memset(out_info, 0, sizeof(wifi6_info_t));
    out_info->bss_color = -1;

    sock = nl_socket_alloc();
    if (!sock) return -ENOMEM;

    if (genl_connect(sock) < 0) {
        nl_socket_free(sock);
        return -ECONNREFUSED;
    }

    family_id = genl_ctrl_resolve(sock, "nl80211");
    if (family_id < 0) {
        nl_socket_free(sock);
        return -ENOENT;
    }

    msg = nlmsg_alloc();
    if (!msg) {
        nl_socket_free(sock);
        return -ENOMEM;
    }

    genlmsg_put(msg, NL_AUTO_PID, NL_AUTO_SEQ, family_id, 0, 0,
               NL80211_CMD_GET_INTERFACE, 0);

    unsigned int ifindex = if_nametoindex(ifname);
    if (ifindex == 0) {
        nlmsg_free(msg);
        nl_socket_free(sock);
        return -ENODEV;
    }

    nla_put_u32(msg, NL80211_ATTR_IFINDEX, ifindex);
    nl_socket_modify_cb(sock, NL_CB_VALID, NL_CB_CUSTOM, parse_nl80211_he_cb, out_info);

    err = nl_send_auto(sock, msg);
    if (err >= 0) {
        nl_recvmsgs_default(sock);
    }

    nlmsg_free(msg);
    nl_socket_free(sock);
    return err < 0 ? err : 0;
}

int main(int argc, char **argv) {
    const char *iface = (argc > 1) ? argv[1] : "wlan0";
    wifi6_info_t info;

    printf("Опитування статусу 802.11ax для інтерфейсу: %s
", iface);
    int res = query_wifi6_status(iface, &info);

    if (res < 0) {
        fprintf(stderr, "Помилка виклику Netlink nl80211: %d
", res);
        return 1;
    }

    printf("Підтримка 802.11ax (HE): %s
", info.has_he_support ? "ТАК" : "НІ");
    if (info.frequency_mhz > 0) {
        printf("Поточна частота каналу: %u МГц
", info.frequency_mhz);
    }
    if (info.bss_color >= 0) {
        printf("Поточний BSS Color: %d
", info.bss_color);
    } else {
        printf("BSS Color: не призначено або не підтримується
");
    }

    return 0;
}
