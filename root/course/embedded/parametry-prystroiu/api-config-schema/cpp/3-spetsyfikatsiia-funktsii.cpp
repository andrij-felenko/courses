namespace embedded::config {

class IConfigurationManager {
public:
    virtual ~IConfigurationManager() = default;

    virtual std::expected<void, Error> initialize() noexcept = 0;

    virtual std::expected<std::uint32_t, Error> get_uint32(std::uint16_t key_id) const noexcept = 0;
    virtual std::expected<std::string_view, Error> get_string(std::uint16_t key_id, std::span<char> buf) const noexcept = 0;

    virtual std::expected<void, Error> validate_candidate(std::span<const std::uint8_t> payload) const noexcept = 0;

    virtual std::expected<void, Error> apply_trial(std::span<const std::uint8_t> candidate_payload,
                                                   std::uint32_t trial_timeout_s) noexcept = 0;

    virtual std::expected<void, Error> confirm_commit() noexcept = 0;
    virtual std::expected<void, Error> abort_rollback() noexcept = 0;

    using MigratorFunction = bool (*)(std::span<const std::uint8_t> old_data,
                                     std::span<std::uint8_t> new_data) noexcept;

    virtual std::expected<void, Error> register_migrator(std::uint16_t from_version,
                                                         std::uint16_t to_version,
                                                         MigratorFunction migrator) noexcept = 0;
};

} // namespace embedded::config
