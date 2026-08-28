/* ==================== Ідіома C (Статичний буфер непрозорого типу) ==================== */
/* channel.h — Публічний заголовок C API */
#ifndef CHANNEL_H
#define CHANNEL_H

#include <stddef.h>
#include <stdint.h>

#define SECURE_CHANNEL_STORAGE_SIZE 128
#define SECURE_CHANNEL_ALIGNMENT 8

typedef struct SecureChannel {
    /* Вирівняний масив байтів фіксованого розміру */
    _Alignas(SECURE_CHANNEL_ALIGNMENT) uint8_t storage[SECURE_CHANNEL_STORAGE_SIZE];
} SecureChannel;

/* Ініціалізація об'єкта безпосередньо у наданій пам'яті (без malloc) */
int secure_channel_init(SecureChannel* chan, const char* peer_addr, uint16_t port);
void secure_channel_destroy(SecureChannel* chan);
int secure_channel_send(SecureChannel* chan, const void* data, size_t len);

#endif /* CHANNEL_H */
