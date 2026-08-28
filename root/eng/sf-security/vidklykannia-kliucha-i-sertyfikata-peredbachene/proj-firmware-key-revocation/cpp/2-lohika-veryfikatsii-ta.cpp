namespace Security {

// Оголошення криптографічних інтерфейсів платформи
bool Sha256(std::span<const std::uint8_t> data, std::span<std::uint8_t, Sha256DigestSize> out_digest) noexcept;
bool EcdsaVerify(std::span<const std::uint8_t, PublicKeySize> pub_key,
                 std::span<const std::uint8_t, Sha256DigestSize> digest,
                 std::span<const std::uint8_t, SignatureSize> signature) noexcept;
bool BurnEfuseBit(HardwareEfuseBank& efuse, std::uint32_t bit_index) noexcept;
bool UpdateMonotonicCounter(HardwareEfuseBank& efuse, std::uint32_t new_version) noexcept;

class SecureBootVerifier {
public:
    static std::expected<void, BootError> AuthorizeFirmware(
        HardwareEfuseBank& efuse,
        const FirmwareHeader& header,
        std::span<const std::uint8_t> payload_data,
        bool auto_burn_version = true) noexcept
    {
        if (header.magic != FwMagic) {
            return std::unexpected(BootError::InvalidMagic);
        }

        if (header.key_slot_index >= OemKeySlots) {
            return std::unexpected(BootError::KeySlotOutOfBounds);
        }

        // 1. Апаратний статус відкликання ключа
        const std::uint32_t slot_mask = 1U << header.key_slot_index;
        if ((efuse.revoked_keys_mask & slot_mask) != 0) {
            return std::unexpected(BootError::KeyRevoked);
        }

        // 2. Звірка гешу публічного ключа з заводським слотом eFuse
        std::array<std::uint8_t, Sha256DigestSize> key_hash{};
        if (!Sha256(header.public_key, key_hash)) {
            return std::unexpected(BootError::KeyHashMismatch);
        }

        const auto& expected_hash = efuse.root_key_hashes[header.key_slot_index];
        if (!std::ranges::equal(key_hash, expected_hash)) {
            return std::unexpected(BootError::KeyHashMismatch);
        }

        // 3. Захист від відкату версії прошивки (Anti-Rollback)
        if (header.fw_version < efuse.monotonic_version) {
            return std::unexpected(BootError::VersionRollback);
        }

        // 4. Перевірка дайджесту образу
        std::array<std::uint8_t, Sha256DigestSize> payload_hash{};
        if (!Sha256(payload_data, payload_hash)) {
            return std::unexpected(BootError::PayloadCorrupted);
        }

        if (!std::ranges::equal(payload_hash, header.payload_sha256)) {
            return std::unexpected(BootError::PayloadCorrupted);
        }

        // 5. Перевірка криптографічного підпису
        if (!EcdsaVerify(header.public_key, payload_hash, header.signature)) {
            return std::unexpected(BootError::SignatureInvalid);
        }

        // 6. Атомарне оновлення апаратного лічильника версії
        if (auto_burn_version && header.fw_version > efuse.monotonic_version) {
            if (!UpdateMonotonicCounter(efuse, header.fw_version)) {
                return std::unexpected(BootError::EfuseBurnFailed);
            }
        }

        return {};
    }

    static std::expected<void, BootError> RevokeKeySlot(
        HardwareEfuseBank& efuse,
        std::uint32_t slot_index) noexcept
    {
        if (slot_index >= OemKeySlots) {
            return std::unexpected(BootError::KeySlotOutOfBounds);
        }

        if (!BurnEfuseBit(efuse, slot_index)) {
            return std::unexpected(BootError::EfuseBurnFailed);
        }

        efuse.revoked_keys_mask |= (1U << slot_index);
        return {};
    }
};

} // namespace Security
