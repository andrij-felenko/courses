namespace embedded::audit {

std::expected<uint32_t, uint64_t> verify_storage_integrity(
    IFlashDriver& flash, 
    const std::array<uint8_t, HashSize>& genesis_hash
) noexcept {
    std::array<uint8_t, HashSize> expected_hash = genesis_hash;
    const uint32_t total_sectors = flash.total_size() / SectorSizeBytes;
    uint32_t verified_count = 0;

    for (uint32_t s = 0; s < total_sectors; ++s) {
        const uint32_t s_addr = s * SectorSizeBytes;
        Record hdr{};
        auto hdr_span = std::as_writable_bytes(std::span{&hdr, 1});
        if (!flash.read(s_addr, std::span<uint8_t>{reinterpret_cast<uint8_t*>(hdr_span.data()), hdr_span.size()})) {
            return std::unexpected(0);
        }
        if (hdr.magic != SectorMagic) continue;

        for (uint32_t slot = 1; slot <= DataSlotsPerSector; ++slot) {
            Record rec{};
            auto rec_span = std::as_writable_bytes(std::span{&rec, 1});
            flash.read(s_addr + slot * RecordSize, std::span<uint8_t>{reinterpret_cast<uint8_t*>(rec_span.data()), rec_span.size()});

            if (rec.magic != MagicSync) {
                return verified_count;
            }

            if (rec.prev_hash != expected_hash) {
                return std::unexpected(rec.sequence_id);
            }

            std::array<uint8_t, HashSize> calc_hash{};
            const auto hashable = std::span<const uint8_t>{
                reinterpret_cast<const uint8_t*>(&rec),
                offsetof(Record, record_hash)
            };
            sha256_compute(hashable, std::span<uint8_t, HashSize>{calc_hash});

            if (rec.record_hash != calc_hash) {
                return std::unexpected(rec.sequence_id);
            }

            expected_hash = calc_hash;
            verified_count++;
        }
    }
    return verified_count;
}

} // namespace embedded::audit
