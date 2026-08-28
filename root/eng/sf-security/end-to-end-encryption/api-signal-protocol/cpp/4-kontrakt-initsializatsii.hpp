// Ініціалізація на боці Аліси (ініціатор сесії)
RatchetStatus ratchet_init_alice(
    RatchetSession               &session,
    std::span<const uint8_t, 32>  shared_master_key,
    std::span<const uint8_t, 32>  bob_dh_public_key
);

// Ініціалізація на боці Боба (відповідач)
RatchetStatus ratchet_init_bob(
    RatchetSession               &session,
    std::span<const uint8_t, 32>  shared_master_key,
    const DhKeyPair              &bob_dh_keypair
);
