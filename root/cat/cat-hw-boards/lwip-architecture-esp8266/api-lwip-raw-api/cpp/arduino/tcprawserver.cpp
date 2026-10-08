#include <lwip/tcp.h>

class TcpRawServer {
public:
    static err_t onAccept(void *arg, struct tcp_pcb *newpcb, err_t err) {
        if (err != ERR_OK || !newpcb) return ERR_VAL;
        tcp_recv(newpcb, [](void *arg, struct tcp_pcb *tpcb, struct pbuf *p, err_t err) -> err_t {
            if (!p) {
                tcp_close(tpcb);
                return ERR_OK;
            }
            tcp_recved(tpcb, p->tot_len);
            pbuf_free(p);
            return ERR_OK;
        });
        return ERR_OK;
    }

    void begin(uint16_t port) {
        struct tcp_pcb *pcb = tcp_new();
        tcp_bind(pcb, IP_ADDR_ANY, port);
        pcb = tcp_listen(pcb);
        tcp_accept(pcb, &TcpRawServer::onAccept);
    }
};
