static uint32_t calc_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320U & -(crc & 1U));
        }
    }
    return ~crc;
}

ml_ota_status_t ml_ota_init(ml_ota_context_t *ctx,
                            const ml_flash_driver_t *flash_drv,
                            uint32_t nv_meta_addr,
                            uint32_t slot_a_addr,
                            uint32_t slot_b_addr,
                            uint32_t max_sram_arena) {
    if (!ctx || !flash_drv) return ML_OTA_ERR_STATE;
    ctx->flash = flash_drv;
    ctx->nv_meta_addr = nv_meta_addr;
    ctx->slot_addrs[0] = slot_a_addr;
    ctx->slot_addrs[1] = slot_b_addr;
    ctx->max_sram_arena = max_sram_arena;
    ctx->session_active = false;
    ctx->received_bytes = 0;

    if (!ctx->flash->read(ctx->nv_meta_addr, (uint8_t*)&ctx->meta, sizeof(ml_nv_metadata_t))) {
        return ML_OTA_ERR_FLASH_IO;
    }

    uint32_t stored_crc = ctx->meta.crc32;
    ctx->meta.crc32 = 0;
    uint32_t computed_crc = calc_crc32((uint8_t*)&ctx->meta, sizeof(ml_nv_metadata_t));
    ctx->meta.crc32 = stored_crc;

    if (ctx->meta.meta_magic != ML_METADATA_MAGIC || stored_crc != computed_crc) {
        ctx->meta.meta_magic = ML_METADATA_MAGIC;
        ctx->meta.sequence_id = 1;
        ctx->meta.active_slot = (uint8_t)ML_SLOT_A;
        ctx->meta.slot_state[ML_SLOT_A] = (uint8_t)ML_STATE_CONFIRMED;
        ctx->meta.slot_state[ML_SLOT_B] = (uint8_t)ML_STATE_EMPTY;
        ctx->meta.trial_boots_remaining = 0;
        ctx->meta.crc32 = 0;
        ctx->meta.crc32 = calc_crc32((uint8_t*)&ctx->meta, sizeof(ml_nv_metadata_t));

        ctx->flash->erase_sector(ctx->nv_meta_addr);
        ctx->flash->write(ctx->nv_meta_addr, (uint8_t*)&ctx->meta, sizeof(ml_nv_metadata_t));
    }

    return ML_OTA_OK;
}

ml_ota_status_t ml_ota_process_chunk(ml_ota_context_t *ctx,
                                     uint32_t offset,
                                     const uint8_t *data,
                                     uint32_t len) {
    if (!ctx || !data || len == 0) return ML_OTA_ERR_STATE;

    if (offset == 0) {
        if (len < sizeof(ml_model_header_t)) return ML_OTA_ERR_INCOMPATIBLE;

        const ml_model_header_t *hdr = (const ml_model_header_t*)data;
        if (hdr->magic != ML_MODEL_MAGIC) return ML_OTA_ERR_INVALID_MAGIC;
        if (hdr->header_version != ML_HEADER_VERSION) return ML_OTA_ERR_INCOMPATIBLE;
        if (hdr->required_arena_size > ctx->max_sram_arena) return ML_OTA_ERR_ARENA_OVERFLOW;
        if (hdr->payload_size > (ML_MODEL_MAX_SIZE - sizeof(ml_model_header_t))) {
            return ML_OTA_ERR_INCOMPATIBLE;
        }

        ctx->target_slot = (ctx->meta.active_slot == ML_SLOT_A) ? ML_SLOT_B : ML_SLOT_A;
        ctx->total_expected_bytes = sizeof(ml_model_header_t) + hdr->payload_size;
        ctx->received_bytes = 0;
        ctx->current_sector_erased = 0;
        ctx->session_active = true;
    }

    if (!ctx->session_active) return ML_OTA_ERR_STATE;
    if (offset != ctx->received_bytes) return ML_OTA_ERR_OFFSET_GAP;
    if (offset + len > ctx->total_expected_bytes) return ML_OTA_ERR_INCOMPATIBLE;

    uint32_t target_base = ctx->slot_addrs[ctx->target_slot];
    uint32_t write_addr = target_base + offset;

    uint32_t start_sector = offset / ML_FLASH_SECTOR_SIZE;
    uint32_t end_sector = (offset + len - 1) / ML_FLASH_SECTOR_SIZE;

    for (uint32_t s = start_sector; s <= end_sector; ++s) {
        if (s >= ctx->current_sector_erased) {
            uint32_t sector_addr = target_base + s * ML_FLASH_SECTOR_SIZE;
            if (!ctx->flash->erase_sector(sector_addr)) {
                ctx->session_active = false;
                return ML_OTA_ERR_FLASH_IO;
            }
            ctx->current_sector_erased = s + 1;
        }
    }

    if (!ctx->flash->write(write_addr, data, len)) {
        ctx->session_active = false;
        return ML_OTA_ERR_FLASH_IO;
    }

    ctx->received_bytes += len;
    return ML_OTA_OK;
}
