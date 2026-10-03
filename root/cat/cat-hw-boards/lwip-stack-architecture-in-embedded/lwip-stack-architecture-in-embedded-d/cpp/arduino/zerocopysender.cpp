#include <lwip/api.h>
#include <lwip/stats.h>

class ZeroCopySender {
private:
    static const char PROGMEM RESPONSE_DATA[];

public:
    static bool sendConstData(netconn* conn) {
        if (!conn) return false;

        // Передача даних без копіювання з прапорцем NETCONN_NOCOPY
        err_t err = netconn_write(conn, RESPONSE_DATA, strlen(RESPONSE_DATA), NETCONN_NOCOPY);
        
        if (err != ERR_OK) {
            checkMemoryStats();
            return false;
        }
        return true;
    }

    static void checkMemoryStats() {
        #if LWIP_STATS
        stats_display();
        #endif
    }
};

const char PROGMEM ZeroCopySender::RESPONSE_DATA[] = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nZero-Copy Data";
