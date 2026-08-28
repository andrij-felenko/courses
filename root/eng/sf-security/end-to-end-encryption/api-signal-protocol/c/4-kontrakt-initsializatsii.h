// Ініціалізація на боці Аліси (ініціатор сесії)
ratchet_status_t ratchet_init_alice(
    ratchet_session_t     *session,
    const uint8_t          shared_master_key[32],
    const uint8_t          bob_dh_public_key[32]
);

// Ініціалізація на боці Боба (відповідач)
ratchet_status_t ratchet_init_bob(
    ratchet_session_t     *session,
    const uint8_t          shared_master_key[32],
    const dh_keypair_t    *bob_dh_keypair
);
