namespace emb::ml {

class OtaUpdater {
public:
    explicit OtaUpdater(const FlashDriver& driver, const OtaConfig& config)
        : driver_(driver), config_(config) {}

    std::expected<void, OtaError> init() {
        NvMetadata temp_meta{};
        auto meta_span = std::span<uint8_t>(reinterpret_cast<uint8_t*>(&temp_meta), sizeof(NvMetadata));
        
        if (!driver_.read(config_.nv_meta_addr, meta_span)) {
            return std::unexpected(OtaError::FlashIoError);
        }

        uint32_t stored_crc = temp_meta.crc32;
        temp_meta.crc32 = 0;
        uint32_t computed_crc = calculate_crc(meta_span);
        temp_meta.crc32 = stored_crc;

        if (temp_meta.meta_magic != kMetaMagic || stored_crc != computed_crc) {
            meta_.meta_magic = kMetaMagic;
            meta_.sequence_id = 1;
            meta_.active_slot = SlotId::SlotA;
            meta_.slot_state[0] = SlotState::Confirmed;
            meta_.slot_state[1] = SlotState::Empty;
            meta_.trial_boots_remaining = 0;
            meta_.crc32 = 0;
            
            auto write_span = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&meta_), sizeof(NvMetadata));
            meta_.crc32 = calculate_crc(write_span);

            driver_.erase_sector(config_.nv_meta_addr);
            driver_.write(config_.nv_meta_addr, write_span);
        } else {
            meta_ = temp_meta;
        }
        return {};
    }

    std::expected<void, OtaError> process_chunk(uint32_t offset, std::span<const uint8_t> data) {
        if (data.empty()) return std::unexpected(OtaError::InvalidState);

        if (offset == 0) {
            if (data.size() < sizeof(ModelHeader)) {
                return std::unexpected(OtaError::IncompatibleSchema);
            }
            const auto* hdr = reinterpret_cast<const ModelHeader*>(data.data());
            if (hdr->magic != kModelMagic) {
                return std::unexpected(OtaError::InvalidMagic);
            }
            if (hdr->required_arena_size > config_.max_sram_arena) {
                return std::unexpected(OtaError::ArenaOverflow);
            }
            target_slot_ = (meta_.active_slot == SlotId::SlotA) ? SlotId::SlotB : SlotId::SlotA;
            total_expected_ = sizeof(ModelHeader) + hdr->payload_size;
            received_bytes_ = 0;
            erased_sectors_ = 0;
            session_active_ = true;
        }

        if (!session_active_) return std::unexpected(OtaError::InvalidState);
        if (offset != received_bytes_) return std::unexpected(OtaError::OffsetGap);

        uint32_t base_addr = config_.slot_addrs[static_cast<size_t>(target_slot_)];
        uint32_t start_sec = offset / kFlashSectorSize;
        uint32_t end_sec = (offset + static_cast<uint32_t>(data.size()) - 1) / kFlashSectorSize;

        for (uint32_t s = start_sec; s <= end_sec; ++s) {
            if (s >= erased_sectors_) {
                if (!driver_.erase_sector(base_addr + s * kFlashSectorSize)) {
                    session_active_ = false;
                    return std::unexpected(OtaError::FlashIoError);
                }
                erased_sectors_ = s + 1;
            }
        }

        if (!driver_.write(base_addr + offset, data)) {
            session_active_ = false;
            return std::unexpected(OtaError::FlashIoError);
        }

        received_bytes_ += static_cast<uint32_t>(data.size());
        return {};
    }

    [[nodiscard]] SlotId active_slot() const noexcept { return meta_.active_slot; }
    [[nodiscard]] SlotId target_slot() const noexcept { return target_slot_; }
    [[nodiscard]] NvMetadata metadata() const noexcept { return meta_; }

private:
    static uint32_t calculate_crc(std::span<const uint8_t> data) {
        uint32_t crc = 0xFFFFFFFFU;
        for (uint8_t byte : data) {
            crc ^= byte;
            for (uint8_t j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320U & -(crc & 1U));
            }
        }
        return ~crc;
    }

    const FlashDriver& driver_;
    const OtaConfig& config_;
    NvMetadata meta_{};
    SlotId target_slot_{SlotId::Invalid};
    uint32_t total_expected_{0};
    uint32_t received_bytes_{0};
    uint32_t erased_sectors_{0};
    bool session_active_{false};
};

} // namespace emb::ml
