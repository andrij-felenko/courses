/* Додавання пакета до кільцевого буфера з оновленням водяної лінії */
bool pbcast_buffer_insert(pbcast_buffer_t *buf, uint64_t seq_num, 
                          const uint8_t *data, uint32_t len) {
    if (len > PBCAST_MAX_PAYLOAD) return false;

    /* Пакет уже старіший за поточну водяну лінію — дублікат */
    if (seq_num <= buf->low_watermark) return false;

    uint64_t offset = seq_num - buf->low_watermark - 1;
    if (offset >= PBCAST_BUFFER_CAPACITY) {
        /* Пакет занадто далеко попереду — буфер переповнено через тривалий розрив */
        return false;
    }

    /* Запис у відповідний слот кільцевого буфера */
    size_t slot_idx = seq_num % PBCAST_BUFFER_CAPACITY;
    pbcast_slot_t *slot = &buf->slots[slot_idx];
    slot->seq_num = seq_num;
    slot->payload_len = len;
    memcpy(slot->payload, data, len);
    slot->valid = true;

    /* Оновлення бітової маски, якщо зміщення в межах 64 бітів */
    if (offset < PBCAST_MASK_BITS) {
        buf->received_mask |= (1ULL << offset);
    }

    /* Просування low_watermark для неперервного ланцюжка отриманих пакетів */
    while (buf->received_mask & 1ULL) {
        buf->low_watermark++;
        buf->received_mask >>= 1;

        /* Підтягування наступного біта за межами поточної 64-бітної маски */
        uint64_t next_check_seq = buf->low_watermark + PBCAST_MASK_BITS;
        size_t next_slot_idx = next_check_seq % PBCAST_BUFFER_CAPACITY;
        if (buf->slots[next_slot_idx].valid && buf->slots[next_slot_idx].seq_num == next_check_seq) {
            buf->received_mask |= (1ULL << (PBCAST_MASK_BITS - 1));
        }
    }

    return true;
}
