#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <arpa/inet.h>
#include <libnetfilter_conntrack/libnetfilter_conntrack.h>

static volatile sig_atomic_t g_stop = 0;

static void handle_signal(int sig) {
    (void)sig;
    g_stop = 1;
}

static void print_ip(uint32_t ip, char *buffer, size_t len) {
    struct in_addr addr;
    addr.s_addr = ip;
    inet_ntop(AF_INET, &addr, buffer, len);
}

static int cb_on_conntrack_event(enum nfct_msg_type type,
                                 struct nf_conntrack *ct,
                                 void *data) {
    (void)data;
    char src_str[INET_ADDRSTRLEN] = {0};
    char dst_str[INET_ADDRSTRLEN] = {0};

    uint8_t proto = nfct_get_attr_u8(ct, ATTR_L4PROTO);
    uint32_t src_ip = nfct_get_attr_u32(ct, ATTR_ORIG_IPV4_SRC);
    uint32_t dst_ip = nfct_get_attr_u32(ct, ATTR_ORIG_IPV4_DST);
    uint16_t src_port = ntohs(nfct_get_attr_u16(ct, ATTR_ORIG_PORT_SRC));
    uint16_t dst_port = ntohs(nfct_get_attr_u16(ct, ATTR_ORIG_PORT_DST));
    uint32_t status = nfct_get_attr_u32(ct, ATTR_STATUS);

    print_ip(src_ip, src_str, sizeof(src_str));
    print_ip(dst_ip, dst_str, sizeof(dst_str));

    const char *event_name = "UNKNOWN";
    switch (type) {
        case NFCT_T_NEW:     event_name = "NEW    "; break;
        case NFCT_T_UPDATE:  event_name = "UPDATE "; break;
        case NFCT_T_DESTROY: event_name = "DESTROY"; break;
        default: break;
    }

    const char *proto_name = (proto == IPPROTO_TCP) ? "TCP" :
                             (proto == IPPROTO_UDP) ? "UDP" : "OTHER";

    printf("[%s] %s %s:%u -> %s:%u (status=0x%08x%s)\n",
           event_name, proto_name,
           src_str, src_port, dst_str, dst_port, status,
           (status & IPS_ASSURED) ? " [ASSURED]" : "");

    return NFCT_CB_CONTINUE;
}

int main(void) {
    struct nfct_handle *handle = NULL;
    int ret = EXIT_FAILURE;

    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);

    handle = nfct_open(NFNL_SUBSYS_CTNETLINK, NFCT_ALL_SYS_GROUP);
    if (!handle) {
        perror("nfct_open failed");
        return EXIT_FAILURE;
    }

    if (nfct_callback_register(handle, NFCT_T_ALL, cb_on_conntrack_event, NULL) < 0) {
        perror("nfct_callback_register failed");
        goto out_close;
    }

    printf("Starting Netfilter Conntrack Monitor... Press Ctrl+C to exit.\n");

    while (!g_stop) {
        int res = nfct_catch(handle);
        if (res < 0) {
            perror("nfct_catch error");
            break;
        }
    }

    ret = EXIT_SUCCESS;

out_close:
    if (handle) {
        nfct_close(handle);
    }
    return ret;
}
