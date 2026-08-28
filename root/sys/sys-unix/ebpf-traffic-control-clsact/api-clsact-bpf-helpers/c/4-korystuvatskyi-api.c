#include <bpf/libbpf.h>

// Опис точки підключення
struct bpf_tc_hook {
    size_t sz;
    int ifindex;
    enum bpf_tc_attach_point attach_point; // BPF_TC_INGRESS, BPF_TC_EGRESS, BPF_TC_CUSTOM
    __u32 parent;
};

// Опції прикріплення фільтра
struct bpf_tc_opts {
    size_t sz;
    int prog_fd;
    __u32 flags;
    __u32 prog_id;
    __u32 handle;
    __u32 priority;
};
