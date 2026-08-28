#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

/* Обробник помилки чистого виклику */
void pure_virtual_trap(void) {
    fprintf(stderr, "FATAL: pure virtual method called!\n");
    abort();
}

typedef struct PacketReceiver PacketReceiver;

typedef struct ReceiverVTable {
    void (*process_payload)(PacketReceiver* self, const uint8_t* data, size_t len);
    void (*cleanup)(PacketReceiver* self);
} ReceiverVTable;

struct PacketReceiver {
    const ReceiverVTable* vptr;
    int socket_fd;
};

/* Спільна допоміжна функція налаштування предка */
void receiver_setup_subsystem(PacketReceiver* self) {
    const uint8_t handshake[4] = {0xAA, 0x55, 0x01, 0x00};
    /* Непрямий виклик через vptr до завершення конструювання нащадка! */
    self->vptr->process_payload(self, handshake, sizeof(handshake));
}

void receiver_base_init(PacketReceiver* self, int fd) {
    static const ReceiverVTable base_vtable = {
        .process_payload = pure_virtual_trap,
        .cleanup = NULL
    };
    /* Встановлюємо таблицю базового типу */
    self->vptr = &base_vtable;
    self->socket_fd = fd;

    /* Викликаємо логіку налаштування */
    receiver_setup_subsystem(self);
}
