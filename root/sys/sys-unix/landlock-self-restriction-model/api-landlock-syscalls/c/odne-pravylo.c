enum landlock_rule_type {
    LANDLOCK_RULE_PATH_BENEATH = 1,
    LANDLOCK_RULE_NET_PORT     = 2,   /* ABI 4 */
};

struct landlock_path_beneath_attr {
    __u64 allowed_access;
    __s32 parent_fd;                  /* зазвичай open(path, O_PATH | O_CLOEXEC) */
} __attribute__((packed));            /* рівно 12 байтів, без вирівнювання */

struct landlock_net_port_attr {
    __u64 allowed_access;
    __u64 port;                       /* порядок байтів вузла, 0…65535 */
};
