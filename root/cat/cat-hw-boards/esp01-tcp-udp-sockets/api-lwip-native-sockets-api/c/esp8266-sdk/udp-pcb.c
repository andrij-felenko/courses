void udp_recv_cb(void *arg, struct udp_pcb *upcb, struct pbuf *p, const ip_addr_t *addr, u16_t port) {
    if (p != NULL) {
        // Обробка корисного навантаження p->payload
        pbuf_free(p);
    }
}

void send_udp_packet(void) {
    struct udp_pcb *upcb = udp_new();
    struct pbuf *p = pbuf_alloc(PBUF_TRANSPORT, 12, PBUF_RAM);
    if (p != NULL) {
        memcpy(p->payload, "Hello UDP", 10);
        ip_addr_t dest_ip;
        IP4_ADDR(&dest_ip, 192, 168, 1, 100);
        udp_sendto(upcb, p, &dest_ip, 1234);
        pbuf_free(p);
    }
    udp_remove(upcb);
}
