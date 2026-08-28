// Шифрування відкритого тексту
std::expected<EncryptedFrame, RatchetStatus> ratchet_encrypt(
    RatchetSession              &session,
    std::span<const uint8_t>     plaintext
);

// Дешифрування зашифрованого кадру
std::expected<std::vector<uint8_t>, RatchetStatus> ratchet_decrypt(
    RatchetSession              &session,
    const MessageHeader         &in_header,
    std::span<const uint8_t>     in_ciphertext
);
