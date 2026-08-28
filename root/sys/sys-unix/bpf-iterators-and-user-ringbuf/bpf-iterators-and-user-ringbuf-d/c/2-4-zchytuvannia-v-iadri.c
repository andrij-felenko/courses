/* Обробка команд із User Ring Buffer у ядрі (Kernel Space, C) */
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>

struct ip_policy {
    __u32 ip_address;
    __u8  action; /* 1 = DROP, 0 = PASS */
};

struct {
    __uint(type, BPF_MAP_TYPE_USER_RINGBUF);
    __uint(max_entries, 512 * 1024);
} user_ringbuf SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 10000);
    __type(key, __u32);
    __type(value, __u8);
} drop_list SEC(".maps");

/* Callback для кожної події з User Ringbuf */
static long handle_policy_update(struct bpf_dynptr *dynptr, void *context)
{
    struct ip_policy policy;

    /* Безпечне зчитування з dynptr з перевіркою меж у runtime */
    if (bpf_dynptr_read(&policy, sizeof(policy), dynptr, 0, 0) < 0)
        return 0;

    if (policy.action == 1) {
        __u8 flag = 1;
        bpf_map_update_elem(&drop_list, &policy.ip_address, &flag, BPF_ANY);
    } else {
        bpf_map_delete_elem(&drop_list, &policy.ip_address);
    }

    return 0;
}

SEC("xdp")
int xdp_firewall(struct xdp_md *ctx)
{
    /* Вичищаємо буфер подій без пробудження userspace */
    bpf_user_ringbuf_drain(&user_ringbuf, handle_policy_update, NULL, BPF_RB_NO_WAKEUP);

    /* Далі виконується звичайна логіка XDP фільтрації */
    return XDP_PASS;
}

char _license[] SEC("license") = "GPL";
