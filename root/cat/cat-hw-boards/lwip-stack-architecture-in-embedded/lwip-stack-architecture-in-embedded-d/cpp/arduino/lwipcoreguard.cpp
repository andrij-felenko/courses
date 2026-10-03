#include <lwip/tcpip.h>
#include <lwip/tcp.h>

class LwipCoreGuard {
public:
    LwipCoreGuard() {
        LOCK_TCPIP_CORE();
    }
    ~LwipCoreGuard() {
        UNLOCK_TCPIP_CORE();
    }
    
    // Заборона копіювання для безпеки RAII
    LwipCoreGuard(const LwipCoreGuard&) = delete;
    LwipCoreGuard& operator=(const LwipCoreGuard&) = delete;
};

class SafeTcpSender {
public:
    static err_t sendDirect(tcp_pcb* pcb, const char* data, uint16_t length) {
        if (pcb == nullptr || data == nullptr) {
            return ERR_ARG;
        }
        
        // Автоматичне захоплення та звільнення локу ядра через RAII
        LwipCoreGuard guard;
        err_t status = tcp_write(pcb, data, length, TCP_WRITE_FLAG_COPY);
        if (status == ERR_OK) {
            status = tcp_output(pcb);
        }
        return status;
    }
};
