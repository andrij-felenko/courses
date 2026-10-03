#include <ESP8266WiFi.h>
#include <lwip/tcp.h>

// Клас асинхронного TCP ECHO-сервера в Arduino C++
class AsyncRawServer {
private:
    struct tcp_pcb* _server_pcb;

    static err_t onRecv(void* arg, struct tcp_pcb* tpcb, struct pbuf* p, err_t err) {
        if (!p) {
            tcp_close(tpcb);
            return ERR_OK;
        }
        // Оновлення ковзного вікна TCP_WND
        tcp_recved(tpcb, p->tot_len);

        // Відправка відповіді
        tcp_write(tpcb, p->payload, p->len, TCP_WRITE_FLAG_COPY);
        tcp_output(tpcb);

        pbuf_free(p);
        return ERR_OK;
    }

    static err_t onAccept(void* arg, struct tcp_pcb* newpcb, err_t err) {
        tcp_recv(newpcb, AsyncRawServer::onRecv);
        return ERR_OK;
    }

public:
    AsyncRawServer() : _server_pcb(nullptr) {}

    bool begin(uint16_t port) {
        _server_pcb = tcp_new();
        if (!_server_pcb) return false;

        if (tcp_bind(_server_pcb, IP_ADDR_ANY, port) != ERR_OK) return false;
        _server_pcb = tcp_listen(_server_pcb);
        tcp_accept(_server_pcb, AsyncRawServer::onAccept);
        Serial.printf("Raw API Server запущено на порту %u\n", port);
        return true;
    }
};
