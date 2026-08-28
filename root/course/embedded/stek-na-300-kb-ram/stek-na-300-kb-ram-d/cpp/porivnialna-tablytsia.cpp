#include <span>
#include <cstdint>
#include <concepts>
#include <memory>

extern "C" {
#include "lwip/opt.h"
#include "lwip/tcp.h"
}

namespace embedded::net {

class TcpEchoServer {
public:
    TcpEchoServer() noexcept = default;
    ~TcpEchoServer() noexcept { stop(); }

    TcpEchoServer(const TcpEchoServer&) = delete;
    TcpEchoServer& operator=(const TcpEchoServer&) = delete;

    [[nodiscard]] bool start(uint16_t port = 7) noexcept {
        struct tcp_pcb* raw_pcb = tcp_new();
        if (raw_pcb == nullptr) {
            return false;
        }

        if (tcp_bind(raw_pcb, IP_ADDR_ANY, port) != ERR_OK) {
            memp_free(MEMP_TCP_PCB, raw_pcb);
            return false;
        }

        listenPcb_ = tcp_listen(raw_pcb);
        tcp_arg(listenPcb_, this);
        tcp_accept(listenPcb_, &TcpEchoServer::onAcceptThunk);
        return true;
    }

    void stop() noexcept {
        if (listenPcb_ != nullptr) {
            tcp_close(listenPcb_);
            listenPcb_ = nullptr;
        }
    }

private:
    static err_t onAcceptThunk(void* arg, struct tcp_pcb* newpcb, err_t err) noexcept {
        if (err != ERR_OK || newpcb == nullptr) {
            return ERR_VAL;
        }
        auto* self = static_cast<TcpEchoServer*>(arg);
        return self->onAccept(newpcb);
    }

    err_t onAccept(struct tcp_pcb* newpcb) noexcept {
        tcp_arg(newpcb, this);
        tcp_recv(newpcb, &TcpEchoServer::onRecvThunk);
        return ERR_OK;
    }

    static err_t onRecvThunk(void* arg, struct tcp_pcb* tpcb, struct pbuf* p, err_t err) noexcept {
        auto* self = static_cast<TcpEchoServer*>(arg);
        return self->onRecv(tpcb, p, err);
    }

    err_t onRecv(struct tcp_pcb* tpcb, struct pbuf* p, err_t err) noexcept {
        if (p == nullptr) {
            tcp_close(tpcb);
            return ERR_OK;
        }

        if (err != ERR_OK) {
            pbuf_free(p);
            return err;
        }

        tcp_recved(tpcb, p->tot_len);

        std::span<const uint8_t> payload{
            static_cast<const uint8_t*>(p->payload),
            p->len
        };

        tcp_write(tpcb, payload.data(), static_cast<u16_t>(payload.size()), TCP_WRITE_FLAG_COPY);
        tcp_output(tpcb);

        pbuf_free(p);
        return ERR_OK;
    }

    struct tcp_pcb* listenPcb_{nullptr};
};

} // namespace embedded::net
