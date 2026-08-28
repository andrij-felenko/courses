/* Звірка локального буфера з отриманим дайджестом та формування списку пропусків */
void pbcast_process_digest(const pbcast_buffer_t *buf,
                           uint64_t remote_watermark, uint64_t remote_mask,
                           uint64_t *out_missing_seqs, size_t *out_missing_count,
                           size_t max_requests) {
    *out_missing_count = 0;

    /* Якщо у віддаленого піра водяна лінія вища за нашу */
    if (remote_watermark > buf->low_watermark) {
        for (uint64_t s = buf->low_watermark + 1; s <= remote_watermark; ++s) {
            uint64_t offset = s - buf->low_watermark - 1;
            bool local_has = (offset < PBCAST_MASK_BITS) ? ((buf->received_mask & (1ULL << offset)) != 0) : false;
            if (!local_has && *out_missing_count < max_requests) {
                out_missing_seqs[(*out_missing_count)++] = s;
            }
        }
    }

    /* Перевірка бітової маски віддаленого піра */
    for (size_t bit = 0; bit < PBCAST_MASK_BITS; ++bit) {
        if (remote_mask & (1ULL << bit)) {
            uint64_t s = remote_watermark + 1 + bit;
            if (s > buf->low_watermark) {
                uint64_t offset = s - buf->low_watermark - 1;
                bool local_has = (offset < PBCAST_MASK_BITS) ? ((buf->received_mask & (1ULL << offset)) != 0) : false;
                if (!local_has && *out_missing_count < max_requests) {
                    out_missing_seqs[(*out_missing_count)++] = s;
                }
            }
        }
    }
}
