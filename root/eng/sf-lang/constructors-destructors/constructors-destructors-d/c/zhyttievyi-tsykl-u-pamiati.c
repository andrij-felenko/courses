#include <stdlib.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    int id;
    char* payload;
} PacketC;

// Явний аналог конструктора
void packet_construct(PacketC* pkt, int id, const char* p) {
    pkt->id = id;
    size_t len = strlen(p) + 1;
    pkt->payload = (char*)malloc(len);
    if (pkt->payload) {
        memcpy(pkt->payload, p, len);
    }
    printf("  Конструктор C Packet #%d\n", pkt->id);
}

// Явний аналог деструктора
void packet_destruct(PacketC* pkt) {
    printf("  Деструктор C Packet #%d\n", pkt->id);
    free(pkt->payload);
    pkt->payload = NULL;
}

void lifecycle_demo_c(void) {
    // 1. Алокація сирої пам'яті під структуру
    _Alignas(PacketC) char raw_storage[sizeof(PacketC)];
    PacketC* pkt = (PacketC*)raw_storage;

    // 2. Ініціалізація сирої пам'яті
    packet_construct(pkt, 42, "Telemetry data");

    // 3. Час життя
    printf("  Payload: %s\n", pkt->payload);

    // 4. Деструкція внутрішніх ресурсів
    packet_destruct(pkt);

    // 5. Деалокація: raw_storage зникає зі стека
}
