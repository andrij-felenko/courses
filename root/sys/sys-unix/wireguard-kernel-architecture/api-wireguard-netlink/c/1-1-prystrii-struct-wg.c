struct wg_device {
    struct net_device *dev;
    struct crypt_queue encrypt_queue;
    struct crypt_queue decrypt_queue;
    struct sock __rcu *sock4;
    struct sock __rcu *sock6;
    struct noise_static_identity static_identity;
    struct allowedips allowedips;
    struct mutex device_update_lock;
    struct list_head peer_list;
    atomic_t device_update_gen;
    u32 incoming_port;
    u32 fwmark;
};
