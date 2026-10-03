#include <ESP8266WiFi.h>
#include <lwip/stats.h>
#include <lwip/tcp.h>

// Клас профілювання пам'яті та діагностики lwIP у C++ (Arduino)
class LwipProfiler {
public:
    static void inspectSystemHealth() {
        Serial.println("--- Системний монітор пам'яті ESP8266 ---");
        Serial.printf("Вільна динамічна купа (DRAM Heap): %u байт\n", ESP.getFreeHeap());
        Serial.printf("Максимальний вільний блок купи   : %u байт\n", ESP.getMaxFreeBlockSize());
        Serial.printf("Фрагментація пам'яті Heap        : %u%%\n", ESP.getHeapFragmentation());

#if LWIP_STATS
        Serial.printf("Помилки виділення PBUF_POOL: %u\n", lwip_stats.memp[MEMP_PBUF_POOL]->err);
        Serial.printf("Помилки виділення TCP_PCB  : %u\n", lwip_stats.memp[MEMP_TCP_PCB]->err);
#endif
    }
};
