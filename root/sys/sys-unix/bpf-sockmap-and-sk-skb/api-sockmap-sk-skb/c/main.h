struct sock_key {
    __u32 sip;
    __u32 dip;
    __u32 sport;
    __u32 dport;
};

struct {
    __uint(type, BPF_MAP_TYPE_SOCKHASH);
    __uint(max_entries, 102400);
    __type(key, struct sock_key);
    __type(value, __u32);
} sock_hash SEC(".maps");
