audit_status_t audit_engine_verify(
    const audit_engine_t *eng,
    uint64_t *out_corrupted_seq,
    uint32_t *out_verified_count
) {
    if (!eng || !eng->is_ready) return AUDIT_ERR_INIT;

    uint8_t expected_hash[AUDIT_HASH_SIZE];
    memset(expected_hash, 0xAA, AUDIT_HASH_SIZE);
    uint32_t total_sectors = eng->hal->total_size / eng->hal->sector_size;
    uint32_t verified = 0;

    for (uint32_t s = 0; s < total_sectors; ++s) {
        uint32_t s_addr = s * eng->hal->sector_size;
        audit_record_t hdr;
        if (eng->hal->read(s_addr, (uint8_t *)&hdr, sizeof(hdr)) != 0) {
            return AUDIT_ERR_FLASH;
        }
        if (hdr.magic != AUDIT_SECTOR_MAGIC) continue;

        for (uint32_t slot = 1; slot <= AUDIT_DATA_SLOTS; ++slot) {
            audit_record_t rec;
            if (eng->hal->read(s_addr + slot * AUDIT_RECORD_SIZE, (uint8_t *)&rec, sizeof(rec)) != 0) {
                return AUDIT_ERR_FLASH;
            }
            if (rec.magic != AUDIT_MAGIC_SYNC) {
                if (out_verified_count) *out_verified_count = verified;
                return AUDIT_OK;
            }

            if (memcmp(rec.prev_hash, expected_hash, AUDIT_HASH_SIZE) != 0) {
                if (out_corrupted_seq) *out_corrupted_seq = rec.sequence_id;
                return AUDIT_ERR_CORRUPT;
            }

            uint8_t calc_hash[AUDIT_HASH_SIZE];
            sha256_calculate((const uint8_t *)&rec, offsetof(audit_record_t, record_hash), calc_hash);

            if (memcmp(rec.record_hash, calc_hash, AUDIT_HASH_SIZE) != 0) {
                if (out_corrupted_seq) *out_corrupted_seq = rec.sequence_id;
                return AUDIT_ERR_CORRUPT;
            }

            memcpy(expected_hash, calc_hash, AUDIT_HASH_SIZE);
            verified++;
        }
    }

    if (out_verified_count) *out_verified_count = verified;
    return AUDIT_OK;
}
