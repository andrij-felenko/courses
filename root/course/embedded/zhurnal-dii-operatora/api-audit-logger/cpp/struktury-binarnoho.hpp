namespace embedded::audit {

#pragma pack(push, 1)

struct Record {
    uint32_t magic{MagicSync};
    uint8_t  version{1};
    uint8_t  flags{0};
    uint8_t  exec_status{static_cast<uint8_t>(ExecStatus::Pending)};
    uint8_t  payload_len{0};
    uint64_t sequence_id{0};
    uint64_t timestamp_utc_ms{0};
    uint64_t operator_id{0};
    uint16_t command_id{0};
    uint8_t  subsystem_id{0};
    uint8_t  padding0{0};
    std::array<uint8_t, MaxPayloadSize> payload{};
    std::array<uint8_t, HashSize> prev_hash{};
    std::array<uint8_t, HashSize> record_hash{};
};
static_assert(sizeof(Record) == RecordSize, "Record struct size must be exactly 128 bytes");

struct SectorHeader {
    uint32_t sector_magic{SectorMagic};
    uint32_t sector_index{0};
    uint64_t base_sequence_id{0};
    std::array<uint8_t, HashSize> start_hash{};
    uint32_t records_count{0xFFFFFFFF};
    std::array<uint8_t, HashSize> end_hash{};
    std::array<uint8_t, 44> reserved{};
};
static_assert(sizeof(SectorHeader) == RecordSize, "SectorHeader struct size must be exactly 128 bytes");

#pragma pack(pop)

} // namespace embedded::audit
