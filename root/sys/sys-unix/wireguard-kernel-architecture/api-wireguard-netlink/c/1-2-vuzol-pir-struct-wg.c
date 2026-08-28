struct wg_peer {
    struct wg_device *wg;
    struct noise_handshake handshake;
    struct noise_keypair __rcu *keypairs;
    struct endpoint endpoint;
    struct allowedips_node node;
    u64 rx_bytes, tx_bytes;
    struct timer_list timer_rekey_retry;
    struct timer_list timer_new_handshake;
    struct timer_list timer_zero_keymaterial;
    struct timer_list timer_persistent_keepalive;
    u16 persistent_keepalive_interval;
    bool timer_need_another_keepalive;
};
