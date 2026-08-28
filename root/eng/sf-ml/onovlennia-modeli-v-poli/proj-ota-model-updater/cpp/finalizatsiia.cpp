namespace emb::ml {

std::expected<void, OtaError> finalize_and_stage(OtaUpdater& updater,
                                                 const FlashDriver& driver,
                                                 const OtaConfig& config,
                                                 NvMetadata& meta,
                                                 SlotId target_slot) {
    uint32_t base_addr = config.slot_addrs[static_cast<size_t>(target_slot)];
    ModelHeader hdr{};
    auto hdr_span = std::span<uint8_t>(reinterpret_cast<uint8_t*>(&hdr), sizeof(ModelHeader));

    if (!driver.read(base_addr, hdr_span)) {
        return std::unexpected(OtaError::FlashIoError);
    }

    meta.sequence_id++;
    meta.active_slot = target_slot;
    meta.slot_state[static_cast<size_t>(target_slot)] = SlotState::Trial;
    meta.trial_boots_remaining = kMaxTrialBoots;
    meta.crc32 = 0;

    auto meta_bytes = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&meta), sizeof(NvMetadata));
    
    uint32_t crc = 0xFFFFFFFFU;
    for (uint8_t b : meta_bytes) {
        crc ^= b;
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320U & -(crc & 1U));
        }
    }
    meta.crc32 = ~crc;

    if (!driver.erase_sector(config.nv_meta_addr)) {
        return std::unexpected(OtaError::FlashIoError);
    }
    if (!driver.write(config.nv_meta_addr, meta_bytes)) {
        return std::unexpected(OtaError::FlashIoError);
    }

    return {};
}

} // namespace emb::ml
