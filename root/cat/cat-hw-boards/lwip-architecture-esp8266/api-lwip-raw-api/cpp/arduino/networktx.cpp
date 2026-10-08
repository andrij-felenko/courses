#include <lwip/tcp.h>
#include <lwip/udp.h>

class NetworkTx {
public:
    static bool sendTcp(struct tcp_pcb *tpcb, const String &data) {
        if (tcp_sndbuf(tpcb) < data.length()) return false;
        tcp_write(tpcb, data.c_str(), data.length(), TCP_WRITE_FLAG_COPY);
        return (tcp_output(tpcb) == ERR_OK);
    }

    static void sendUdp(const ip_addr_t &ip, uint16_t port, const uint8_t *buf, size_t size) {
        struct udp_pcb *upcb = udp_new();
        struct pbuf *p = pbuf_alloc(PBUF_TRANSPORT, size, PBUF_RAM);
        if (p) {
            memcpy(p->payload, buf, size);
            udp_sendto(upcb, p, &ip, port);
            pbuf_free(p);
        }
        udp_remove(upcb);
    }
};
