// Шифрування відкритого тексту
ratchet_status_t ratchet_encrypt(
    ratchet_session_t     *session,
    const uint8_t         *plaintext,
    size_t                 plaintext_len,
    message_header_t      *out_header,
    uint8_t               *out_ciphertext,
    size_t                *out_ciphertext_len
);

// Дешифрування зашифрованого кадру
ratchet_status_t ratchet_decrypt(
    ratchet_session_t     *session,
    const message_header_t *in_header,
    const uint8_t         *in_ciphertext,
    size_t                 in_ciphertext_len,
    uint8_t               *out_plaintext,
    size_t                *out_plaintext_len
);
