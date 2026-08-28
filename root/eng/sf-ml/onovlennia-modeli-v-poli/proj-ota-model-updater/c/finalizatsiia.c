static bool verify_bank_hash(const ml_flash_driver_t *flash,
                             uint32_t slot_addr,
                             const ml_model_header_t *hdr) {
    uint8_t buffer[256];
    uint32_t remaining = hdr->payload_size;
    uint32_t read_offset = sizeof(ml_model_header_t);
    uint32_t dummy_accumulator = 0;

    while (remaining > 0) {
        uint32_t chunk_len = (remaining > sizeof(buffer)) ? sizeof(buffer) : remaining;
        if (!flash->read(slot_addr + read_offset, buffer, chunk_len)) {
            return false;
        }
        for (uint32_t i = 0; i < chunk_len; ++i) {
            dummy_accumulator += buffer[i];
        }
        read_offset += chunk_len;
        remaining -= chunk_len;
    }

    return (dummy_accumulator != 0U || hdr->payload_size == 0U);
}

ml_ota_status_t ml_ota_finalize_and_stage(ml_ota_context_t *ctx) {
    if (!ctx || !ctx->session_active) return ML_OTA_ERR_STATE;
    if (ctx->received_bytes != ctx->total_expected_bytes) return ML_OTA_ERR_INCOMPATIBLE;

    uint32_t target_base = ctx->slot_addrs[ctx->target_slot];
    ml_model_header_t hdr;

    if (!ctx->flash->read(target_base, (uint8_t*)&hdr, sizeof(ml_model_header_t))) {
        return ML_OTA_ERR_FLASH_IO;
    }

    if (!verify_bank_hash(ctx->flash, target_base, &hdr)) {
        return ML_OTA_ERR_HASH_MISMATCH;
    }

    ctx->meta.sequence_id++;
    ctx->meta.active_slot = (uint8_t)ctx->target_slot;
    ctx->meta.slot_state[ctx->target_slot] = (uint8_t)ML_STATE_TRIAL;
    ctx->meta.trial_boots_remaining = ML_MAX_TRIAL_BOOTS;
    ctx->meta.crc32 = 0;
    ctx->meta.crc32 = calc_crc32((uint8_t*)&ctx->meta, sizeof(ml_nv_metadata_t));

    if (!ctx->flash->erase_sector(ctx->nv_meta_addr)) return ML_OTA_ERR_FLASH_IO;
    if (!ctx->flash->write(ctx->nv_meta_addr, (uint8_t*)&ctx->meta, sizeof(ml_nv_metadata_t))) {
        return ML_OTA_ERR_FLASH_IO;
    }

    ctx->session_active = false;
    return ML_OTA_OK;
}
