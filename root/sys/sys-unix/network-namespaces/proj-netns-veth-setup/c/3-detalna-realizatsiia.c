#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sched.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <linux/rtnetlink.h>
#include <net/if.h>

#define NETNS_PATH "/var/run/netns/demo_c_ns"

/* Структура запиту Netlink для створення veth-пари */
struct veth_req {
    struct nlmsghdr nlh;
    struct ifinfomsg ifm;
    char buf[1024];
};

static int create_veth_pair(int netlink_fd, const char *veth_host, const char *veth_ns, int target_ns_fd) {
    struct veth_req req;
    memset(&req, 0, sizeof(req));

    req.nlh.nlmsg_len = NLMSG_LENGTH(sizeof(struct ifinfomsg));
    req.nlh.nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK;
    req.nlh.nlmsg_type = RTM_NEWLINK;
    req.ifm.ifi_family = AF_UNSPEC;

    /* Додавання IFLA_IFNAME для хостового кінця */
    struct rtattr *rta = (struct rtattr *)(((char *)&req) + req.nlh.nlmsg_len);
    rta->rta_type = IFLA_IFNAME;
    rta->rta_len = RTA_LENGTH(strlen(veth_host) + 1);
    strcpy(RTA_DATA(rta), veth_host);
    req.nlh.nlmsg_len = NLMSG_ALIGN(req.nlh.nlmsg_len) + RTA_ALIGN(rta->rta_len);

    /* Додавання IFLA_LINKINFO */
    struct rtattr *linkinfo = (struct rtattr *)(((char *)&req) + req.nlh.nlmsg_len);
    linkinfo->rta_type = IFLA_LINKINFO;
    linkinfo->rta_len = RTA_LENGTH(0);

    /* IFLA_INFO_KIND -> "veth" */
    struct rtattr *kind = (struct rtattr *)(((char *)linkinfo) + RTA_LENGTH(0));
    kind->rta_type = IFLA_INFO_KIND;
    kind->rta_len = RTA_LENGTH(5);
    strcpy(RTA_DATA(kind), "veth");
    linkinfo->rta_len += RTA_ALIGN(kind->rta_len);

    /* IFLA_INFO_DATA для налаштування peer */
    struct rtattr *data = (struct rtattr *)(((char *)kind) + RTA_ALIGN(kind->rta_len));
    data->rta_type = IFLA_INFO_DATA;
    data->rta_len = RTA_LENGTH(0);

    /* VETH_INFO_PEER Header */
    struct rtattr *peer = (struct rtattr *)(((char *)data) + RTA_LENGTH(0));
    peer->rta_type = 1; /* VETH_INFO_PEER */
    peer->rta_len = RTA_LENGTH(sizeof(struct ifinfomsg));
    
    struct ifinfomsg *peer_ifm = (struct ifinfomsg *)RTA_DATA(peer);
    memset(peer_ifm, 0, sizeof(*peer_ifm));
    peer_ifm->ifi_family = AF_UNSPEC;

    /* Peer IFLA_IFNAME */
    struct rtattr *peer_name = (struct rtattr *)(((char *)peer) + RTA_LENGTH(sizeof(struct ifinfomsg)));
    peer_name->rta_type = IFLA_IFNAME;
    peer_name->rta_len = RTA_LENGTH(strlen(veth_ns) + 1);
    strcpy(RTA_DATA(peer_name), veth_ns);
    peer->rta_len += RTA_ALIGN(peer_name->rta_len);

    /* Peer IFLA_NET_NS_FD - відразу поміщаємо peer у цільовий netns */
    struct rtattr *peer_ns = (struct rtattr *)(((char *)peer_name) + RTA_ALIGN(peer_name->rta_len));
    peer_ns->rta_type = IFLA_NET_NS_FD;
    peer_ns->rta_len = RTA_LENGTH(sizeof(int));
    *(int *)RTA_DATA(peer_ns) = target_ns_fd;
    peer->rta_len += RTA_ALIGN(peer_ns->rta_len);

    data->rta_len += RTA_ALIGN(peer->rta_len);
    linkinfo->rta_len += RTA_ALIGN(data->rta_len);
    req.nlh.nlmsg_len = NLMSG_ALIGN(req.nlh.nlmsg_len) + RTA_ALIGN(linkinfo->rta_len);

    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;

    if (sendto(netlink_fd, &req, req.nlh.nlmsg_len, 0, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("sendto(rtnetlink)");
        return -1;
    }
    return 0;
}

int main(void) {
    int orig_ns_fd = open("/proc/self/ns/net", O_RDONLY);
    if (orig_ns_fd < 0) {
        perror("open(orig_ns)");
        return 1;
    }

    mkdir("/var/run/netns", 0755);
    int touch_fd = open(NETNS_PATH, O_CREAT | O_RDWR | O_EXCL, 0644);
    if (touch_fd >= 0) close(touch_fd);

    if (unshare(CLONE_NEWNET) != 0) {
        perror("unshare(CLONE_NEWNET)");
        close(orig_ns_fd);
        return 1;
    }

    if (mount("/proc/self/ns/net", NETNS_PATH, NULL, MS_BIND, NULL) != 0) {
        perror("mount bind netns");
    }

    int new_ns_fd = open(NETNS_PATH, O_RDONLY);

    /* Повертаємося в початковий простір для створення veth-пари.
       Без цієї перевірки програма мовчки лишилася б у новому просторі
       і створила б обидва кінці пари не там, де треба. */
    if (setns(orig_ns_fd, CLONE_NEWNET) != 0) {
        perror("setns(orig_ns)");
        if (new_ns_fd >= 0) close(new_ns_fd);
        close(orig_ns_fd);
        return 1;
    }

    int nl_fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
    if (nl_fd >= 0 && new_ns_fd >= 0) {
        if (create_veth_pair(nl_fd, "veth-host", "veth-ns", new_ns_fd) == 0) {
            /* Запит надіслано; чи справді пара створена, покаже
               NLMSG_ERROR-відповідь ядра — розбір див. у §5 */
            printf("Запит на створення veth-пари надіслано (netns '%s')\n", NETNS_PATH);
        }
        close(nl_fd);
    }

    if (new_ns_fd >= 0) close(new_ns_fd);
    close(orig_ns_fd);
    return 0;
}
