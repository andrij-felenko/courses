/* main.c — Реалізація мовою C (libbpf) */
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <bpf/libbpf.h>
#include "packet_probe.skel.h"

static volatile sig_atomic_t exiting = 0;

static void sig_handler(int sig)
{
    exiting = 1;
}

struct event_t {
    unsigned long long skb_addr;
    unsigned long long latency_softirq_us;
    unsigned long long latency_netfilter_us;
    unsigned long long latency_total_us;
    unsigned int src_ip;
    unsigned int dst_ip;
    unsigned short src_port;
    unsigned short dst_port;
    unsigned short protocol;
    unsigned int drop_reason;
    char ifname[16];
};

static const char *get_drop_reason_str(unsigned int reason)
{
    switch (reason) {
    case 0: return "DELIVERED_OK";
    case 1: return "NOT_SPECIFIED";
    case 2: return "NO_SOCKET";
    case 3: return "PKT_TOO_SMALL";
    case 4: return "TCP_CSUM";
    case 5: return "SOCKET_RCVBUFF";
    case 8: return "NETFILTER_DROP";
    case 10: return "IP_INADDRERRORS";
    case 32: return "XDP_DROP";
    case 36: return "TC_INGRESS_DROP";
    default: return "OTHER_REASON";
    }
}

static int handle_event(void *ctx, void *data, size_t data_sz)
{
    const struct event_t *e = data;
    if (data_sz < sizeof(*e))
        return 0;

    printf("[SKB 0x%llx] Total Latency: %6llu us | Status: %-16s | DropCode: %u\n",
           e->skb_addr, e->latency_total_us, get_drop_reason_str(e->drop_reason), e->drop_reason);
    return 0;
}

int main(int argc, char **argv)
{
    struct packet_probe_bpf *skel = NULL;
    struct ring_buffer *rb = NULL;
    int err = 0;

    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    skel = packet_probe_bpf__open_and_load();
    if (!skel) {
        fprintf(stderr, "Помилка відкриття та завантаження BPF скелета\n");
        return 1;
    }

    err = packet_probe_bpf__attach(skel);
    if (err) {
        fprintf(stderr, "Помилка прикріплення BPF програм: %d\n", err);
        goto cleanup;
    }

    rb = ring_buffer__new(bpf_map__fd(skel->maps.events), handle_event, NULL, NULL);
    if (!rb) {
        fprintf(stderr, "Помилка створення Ring Buffer\n");
        goto cleanup;
    }

    printf("%-20s %-22s %-18s %s\n", "SKB Pointer", "Total Traversal Time", "Kernel Verdict", "Reason ID");
    printf("--------------------------------------------------------------------------------\n");

    while (!exiting) {
        err = ring_buffer__poll(rb, 100 /* timeout_ms */);
        if (err < 0 && err != -4 /* EINTR */) {
            fprintf(stderr, "Помилка опитування кільцевого буфера: %d\n", err);
            break;
        }
    }

cleanup:
    if (rb)
        ring_buffer__free(rb);
    if (skel)
        packet_probe_bpf__destroy(skel);
    printf("\nТрасування завершено.\n");
    return 0;
}
