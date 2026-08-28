struct allowedips_node {
    struct wg_peer __rcu *peer;
    struct allowedips_node __rcu *bit[2];
    u8 cidr;
    u8 bit_at;
    u8 ip[16];
};

struct allowedips {
    struct allowedips_node __rcu *root4;
    struct allowedips_node __rcu *root6;
    struct mutex mutex;
};
