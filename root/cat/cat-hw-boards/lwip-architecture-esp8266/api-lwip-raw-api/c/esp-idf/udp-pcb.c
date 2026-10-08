#include "lwip/tcp.h"
#include "lwip/udp.h"

void send_tcp_data(struct tcp_pcb *tpcb, const char *msg, uint16_t len) {
    if (tcp_sndbuf(tpcb) >= len) {
        tcp_write(tpcb, msg, len, TCP_WRITE_FLAG_COPY);
        tcp_output(tpcb);
    }
}

void send_udp_packet(ip_addr_t *dest_ip, uint16_t port, const void *data, uint16_t len) {
    struct udp_pcb *upcb = udp_new();
    struct pbuf *p = pbuf_alloc(PBUF_TRANSPORT, len, PBUF_RAM);
    if (p != NULL) {
        memcpy(p->payload, data, len);
        udp_sendto(upcb, p, dest_ip, port);
        pbuf_free(p);
    }
    udp_remove(upcb);
}
