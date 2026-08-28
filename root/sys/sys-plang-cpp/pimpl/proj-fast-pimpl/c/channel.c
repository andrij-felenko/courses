/* ==================== C: channel.c ==================== */
#include "channel.h"
#include <string.h>
#include <assert.h>

/* Повна внутрішня структура в .c файлі */
typedef struct ChannelInternal {
    uint8_t session_key[32];
    uint64_t sequence_number;
    uint64_t total_bytes;
    uint16_t port;
    int is_connected;
} ChannelInternal;

int secure_channel_init(SecureChannel* chan, const char* peer_addr, uint16_t port) {
    /* Перевірка на етапі компіляції чи вистачає буфера */
    static_assert(sizeof(ChannelInternal) <= SECURE_CHANNEL_STORAGE_SIZE, 
                  "Буфер SecureChannel замалий!");
    static_assert(_Alignof(ChannelInternal) <= SECURE_CHANNEL_ALIGNMENT, 
                  "Невідповідність вирівнювання ChannelInternal!");

    ChannelInternal* internal = (ChannelInternal*)chan->storage;
    memset(internal->session_key, 0xAA, sizeof(internal->session_key));
    internal->sequence_number = 0;
    internal->total_bytes = 0;
    internal->port = port;
    internal->is_connected = 1;
    return 0;
}

void secure_channel_destroy(SecureChannel* chan) {
    ChannelInternal* internal = (ChannelInternal*)chan->storage;
    /* Очищення конфіденційних ключів у пам'яті */
    memset(internal, 0, sizeof(ChannelInternal));
}

int secure_channel_send(SecureChannel* chan, const void* data, size_t len) {
    ChannelInternal* internal = (ChannelInternal*)chan->storage;
    if (!internal->is_connected) return -1;
    internal->total_bytes += len;
    internal->sequence_number++;
    return 0;
}
