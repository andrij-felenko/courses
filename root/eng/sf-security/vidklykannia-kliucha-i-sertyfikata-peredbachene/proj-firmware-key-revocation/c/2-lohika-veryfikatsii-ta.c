/* Допоміжні функції криптографії (заглушки для стандартизованих крипторушіїв) */
bool crypto_sha256(const uint8_t *data, size_t len, uint8_t *digest_out);
bool crypto_ecdsa_verify(const uint8_t *pub_key, const uint8_t *digest, const uint8_t *signature);
bool hardware_burn_efuse_bit(HardwareEfuseBank *efuse, uint32_t bit_index);
bool hardware_update_monotonic_counter(HardwareEfuseBank *efuse, uint32_t new_version);

BootResult verify_and_authorize_firmware(
    HardwareEfuseBank *efuse,
    const FirmwareHeader *header,
    const uint8_t *payload_data,
    bool auto_burn_version)
{
    if (header->magic != FW_MAGIC) {
        return BOOT_ERR_INVALID_MAGIC;
    }

    if (header->key_slot_index >= OEM_KEY_SLOTS) {
        return BOOT_ERR_KEY_SLOT_OUT_OF_BOUNDS;
    }

    /* 1. Перевірка бітової маски відкликання eFuse */
    if ((efuse->revoked_keys_mask & (1U << header->key_slot_index)) != 0) {
        return BOOT_ERR_KEY_REVOKED;
    }

    /* 2. Звірка гешу публічного ключа з апаратним слотом */
    uint8_t computed_key_hash[SHA256_DIGEST_SIZE];
    if (!crypto_sha256(header->public_key, sizeof(header->public_key), computed_key_hash)) {
        return BOOT_ERR_KEY_HASH_MISMATCH;
    }

    if (memcmp(computed_key_hash, efuse->root_key_hashes[header->key_slot_index], SHA256_DIGEST_SIZE) != 0) {
        return BOOT_ERR_KEY_HASH_MISMATCH;
    }

    /* 3. Перевірка версії проти апаратного лічильника відкату */
    if (header->fw_version < efuse->monotonic_version) {
        return BOOT_ERR_VERSION_ROLLBACK;
    }

    /* 4. Перевірка цілісності корисного навантаження */
    uint8_t computed_payload_hash[SHA256_DIGEST_SIZE];
    if (!crypto_sha256(payload_data, header->payload_length, computed_payload_hash)) {
        return BOOT_ERR_PAYLOAD_CORRUPTED;
    }

    if (memcmp(computed_payload_hash, header->payload_sha256, SHA256_DIGEST_SIZE) != 0) {
        return BOOT_ERR_PAYLOAD_CORRUPTED;
    }

    /* 5. Перевірка криптографічного підпису образу */
    if (!crypto_ecdsa_verify(header->public_key, computed_payload_hash, header->signature)) {
        return BOOT_ERR_SIGNATURE_INVALID;
    }

    /* 6. Якщо версія новіша і підтверджена — спалюємо біти лічильника відкату */
    if (auto_burn_version && header->fw_version > efuse->monotonic_version) {
        if (!hardware_update_monotonic_counter(efuse, header->fw_version)) {
            return BOOT_ERR_EFUSE_BURN_FAILED;
        }
    }

    return BOOT_OK;
}

/* Функція екстреного або планового анулювання скомпрометованого ключа */
BootResult revoke_key_slot(HardwareEfuseBank *efuse, uint32_t slot_to_revoke)
{
    if (slot_to_revoke >= OEM_KEY_SLOTS) {
        return BOOT_ERR_KEY_SLOT_OUT_OF_BOUNDS;
    }

    /* Спалюємо відповідний біт eFuse (однобічна операція 0 -> 1) */
    if (!hardware_burn_efuse_bit(efuse, slot_to_revoke)) {
        return BOOT_ERR_EFUSE_BURN_FAILED;
    }

    efuse->revoked_keys_mask |= (1U << slot_to_revoke);
    return BOOT_OK;
}
