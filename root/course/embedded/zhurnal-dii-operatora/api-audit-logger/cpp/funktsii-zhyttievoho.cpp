namespace embedded::audit {

class AuditLogger {
public:
    explicit AuditLogger(IFlashStorage& storage) noexcept;
    ~AuditLogger() = default;

    AuditLogger(const AuditLogger&) = delete;
    AuditLogger& operator=(const AuditLogger&) = delete;
    AuditLogger(AuditLogger&&) noexcept = default;
    AuditLogger& operator=(AuditLogger&&) noexcept = default;

    [[nodiscard]] std::expected<void, Status> init() noexcept;

    [[nodiscard]] std::expected<uint64_t, Status> record_command(
        uint64_t timestamp_utc_ms,
        uint64_t operator_id,
        uint16_t command_id,
        uint8_t subsystem_id,
        RecordFlags flags,
        std::span<const uint8_t> payload
    ) noexcept;

    [[nodiscard]] std::expected<void, Status> update_ack(
        uint64_t target_seq_id,
        uint64_t timestamp_utc_ms,
        ExecStatus exec_status,
        uint32_t error_code
    ) noexcept;

    [[nodiscard]] std::expected<void, uint64_t> verify_chain() const noexcept;

    [[nodiscard]] uint64_t current_sequence_id() const noexcept { return current_seq_id_; }
    [[nodiscard]] std::span<const uint8_t, HashSize> latest_hash() const noexcept { return last_hash_; }

private:
    IFlashStorage& storage_;
    uint64_t current_seq_id_{0};
    uint32_t active_sector_idx_{0};
    uint32_t next_slot_offset_{0};
    std::array<uint8_t, HashSize> last_hash_{};
    bool initialized_{false};

    std::expected<void, Status> scan_sectors() noexcept;
    std::expected<void, Status> rotate_sector() noexcept;
};

} // namespace embedded::audit
