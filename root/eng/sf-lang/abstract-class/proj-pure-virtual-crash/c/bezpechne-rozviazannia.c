#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef struct PacketReceiver PacketReceiver;

typedef struct ReceiverVTable {
    void (*process_payload)(PacketReceiver* self, const uint8_t* data, size_t len);
    void (*destroy)(PacketReceiver* self);
} ReceiverVTable;

struct PacketReceiver {
    const ReceiverVTable* vptr;
    int socket_fd;
};

typedef struct TelemetryReceiver {
    PacketReceiver base;
    uint64_t processed_packets;
} TelemetryReceiver;

static void telemetry_process(PacketReceiver* self_base, const uint8_t* data, size_t len) {
    TelemetryReceiver* self = (TelemetryReceiver*)self_base;
    self->processed_packets++;
    printf("Пакет телеметрії #%lu успішно розібрано, байтів: %zu\n", self->processed_packets, len);
}

static void telemetry_destroy(PacketReceiver* self_base) {
    free(self_base);
}

static const ReceiverVTable g_telemetry_vtable = {
    .process_payload = telemetry_process,
    .destroy = telemetry_destroy
};

/* Безпечна фабрика створення */
PacketReceiver* telemetry_receiver_create(int socket_fd) {
    TelemetryReceiver* obj = (TelemetryReceiver*)malloc(sizeof(TelemetryReceiver));
    if (!obj) return NULL;

    obj->base.vptr = &g_telemetry_vtable;
    obj->base.socket_fd = socket_fd;
    obj->processed_packets = 0;

    /* Безпечний виклик: таблиця конкретного нащадка гарантовано встановлена */
    const uint8_t handshake[4] = {0xAA, 0x55, 0x01, 0x00};
    obj->base.vptr->process_payload((PacketReceiver*)obj, handshake, sizeof(handshake));

    return (PacketReceiver*)obj;
}
