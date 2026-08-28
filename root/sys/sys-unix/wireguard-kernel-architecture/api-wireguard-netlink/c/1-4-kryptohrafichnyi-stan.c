struct noise_handshake {
    struct noise_static_identity *static_identity;
    u8 prk[NOISE_HASH_LEN];
    u8 hash[NOISE_HASH_LEN];
    u8 chaining_key[NOISE_HASH_LEN];
    u8 remote_static[NOISE_PUBLIC_KEY_LEN];
    u8 remote_ephemeral[NOISE_PUBLIC_KEY_LEN];
    u8 ephemeral_private[NOISE_PUBLIC_KEY_LEN];
    u8 remote_preshared_key[NOISE_SYMMETRIC_KEY_LEN];
    enum handshake_state state;
    u32 local_index;
    u32 remote_index;
    u64 last_sent_handshake;
};
