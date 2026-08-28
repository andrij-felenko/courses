bool ml_boot_validate_or_rollback(ml_ota_context_t *ctx,
                                  bool (*model_self_test_fn)(const uint8_t *model_data, uint32_t size)) {
    if (!ctx) return false;

    ml_slot_id_t current = (ml_slot_id_t)ctx->meta.active_slot;
    if (ctx->meta.slot_state[current] == ML_STATE_CONFIRMED) {
        return true;
    }

    if (ctx->meta.slot_state[current] == ML_STATE_TRIAL) {
        uint32_t model_base = ctx->slot_addrs[current] + sizeof(ml_model_header_t);
        const ml_model_header_t *hdr = (const ml_model_header_t*)ctx->slot_addrs[current];

        bool test_passed = false;
        if (model_self_test_fn) {
            test_passed = model_self_test_fn((const uint8_t*)model_base, hdr->payload_size);
        }

        if (test_passed) {
            ctx->meta.slot_state[current] = ML_STATE_CONFIRMED;
            ctx->meta.trial_boots_remaining = 0;
        } else {
            if (ctx->meta.trial_boots_remaining > 1) {
                ctx->meta.trial_boots_remaining--;
            } else {
                ml_slot_id_t fallback = (current == ML_SLOT_A) ? ML_SLOT_B : ML_SLOT_A;
                ctx->meta.active_slot = (uint8_t)fallback;
                ctx->meta.slot_state[current] = ML_STATE_FAILED;
                ctx->meta.trial_boots_remaining = 0;
            }
        }

        ctx->meta.sequence_id++;
        ctx->meta.crc32 = 0;
        ctx->meta.crc32 = calc_crc32((uint8_t*)&ctx->meta, sizeof(ml_nv_metadata_t));
        ctx->flash->erase_sector(ctx->nv_meta_addr);
        ctx->flash->write(ctx->nv_meta_addr, (uint8_t*)&ctx->meta, sizeof(ml_nv_metadata_t));

        return test_passed;
    }

    return false;
}
