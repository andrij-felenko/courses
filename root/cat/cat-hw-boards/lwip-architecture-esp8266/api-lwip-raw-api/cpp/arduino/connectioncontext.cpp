#include <lwip/tcp.h>

struct ConnectionContext {
    struct tcp_pcb *pcb;
    uint32_t lastActivity;
};

class TcpSafety {
public:
    static void onError(void *arg, err_t err) {
        ConnectionContext *ctx = static_cast<ConnectionContext*>(arg);
        if (ctx) {
            ctx->pcb = nullptr; // PCB вже знищено стеком
            delete ctx;
        }
    }

    static err_t onPoll(void *arg, struct tcp_pcb *tpcb) {
        ConnectionContext *ctx = static_cast<ConnectionContext*>(arg);
        if (!ctx || (millis() - ctx->lastActivity > 10000)) {
            tcp_abort(tpcb);
            return ERR_ABRT; // Інформуємо lwIP про анулювання PCB
        }
        return ERR_OK;
    }

    static void bindSafety(struct tcp_pcb *pcb, ConnectionContext *ctx) {
        ctx->pcb = pcb;
        ctx->lastActivity = millis();
        tcp_arg(pcb, ctx);
        tcp_err(pcb, &TcpSafety::onError);
        tcp_poll(pcb, &TcpSafety::onPoll, 2); // Виклик кожну 1 секунду
    }
};
