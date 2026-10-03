#include <ESP8266WiFi.h>
#include <lwip/tcp.h>

// Клас керування потоком даних TCP у середовищі Arduino C++
class WindowFlowController {
public:
    static err_t handleReceive(void *arg, struct tcp_pcb *tpcb, struct pbuf *p, err_t err) {
        if (!p) {
            tcp_close(tpcb);
            return ERR_OK;
        }

        uint16_t len = p->tot_len;
        Serial.printf("Прийнято кадр tot_len = %u. Доступне вікно rcv_wnd = %u\n", len, tpcb->rcv_wnd);

        // Оновлення ковзного вікна в TCB
        tcp_recved(tpcb, len);

        // Перевірка залишкового обсягу вихідного буфера
        uint16_t snd_space = tcp_sndbuf(tpcb);
        Serial.printf("Доступний буфер передачі snd_buf = %u байт\n", snd_space);

        // Звільнення пакетного буфера pbuf
        pbuf_free(p);
        return ERR_OK;
    }
};
