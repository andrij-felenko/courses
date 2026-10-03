#include <ESP8266WiFi.h>
#include <lwip/netif.h>

// Клас для моніторингу низькорівневих параметрів netif у C++ (Arduino)
class NetifMonitor {
public:
    static void printDetails() {
        struct netif *nif = netif_list; // Голова списку всіх реєстрацій netif

        while (nif != nullptr) {
            Serial.printf("Інтерфейс: %c%c%u, Стан: %s\n",
                          nif->name[0], nif->name[1], nif->num,
                          (nif->flags & NETIF_FLAG_UP) ? "UP" : "DOWN");

            IPAddress ip(nif->ip_addr.addr);
            Serial.print("  IP Address: ");
            Serial.println(ip);

            nif = nif->next; // Перехід до наступного мережевого адаптера списку
        }
    }
};
