namespace emb::ml {

template <typename SelfTestCallable>
bool boot_validate_or_rollback(const FlashDriver& driver,
                               const OtaConfig& config,
                               NvMetadata& meta,
                               SelfTestCallable&& self_test) {
    auto current_idx = static_cast<size_t>(meta.active_slot);
    if (meta.slot_state[current_idx] == SlotState::Confirmed) {
        return true;
    }

    if (meta.slot_state[current_idx] == SlotState::Trial) {
        uint32_t model_base = config.slot_addrs[current_idx] + sizeof(ModelHeader);
        
        bool passed = self_test(model_base);
        if (passed) {
            meta.slot_state[current_idx] = SlotState::Confirmed;
            meta.trial_boots_remaining = 0;
        } else {
            if (meta.trial_boots_remaining > 1) {
                meta.trial_boots_remaining--;
            } else {
                meta.active_slot = (meta.active_slot == SlotId::SlotA) ? SlotId::SlotB : SlotId::SlotA;
                meta.slot_state[current_idx] = SlotState::Failed;
                meta.trial_boots_remaining = 0;
            }
        }

        meta.sequence_id++;
        auto meta_bytes = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&meta), sizeof(NvMetadata));
        
        uint32_t crc = 0xFFFFFFFFU;
        for (uint8_t b : meta_bytes) {
            crc ^= b;
            for (uint8_t j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320U & -(crc & 1U));
            }
        }
        meta.crc32 = ~crc;

        driver.erase_sector(config.nv_meta_addr);
        driver.write(config.nv_meta_addr, meta_bytes);
        return passed;
    }

    return false;
}

} // namespace emb::ml
