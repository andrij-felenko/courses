/* deny-net.bpf.c */
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

#define AF_UNIX 1        /* у vmlinux.h нема сталих простору користувача */
#define EPERM   1

char LICENSE[] SEC("license") = "GPL";

struct {
	__uint(type, BPF_MAP_TYPE_HASH);
	__uint(max_entries, 64);
	__type(key, __u64);              /* ідентифікатор cgroup */
	__type(value, __u8);
} caged SEC(".maps");

SEC("lsm/socket_create")
int BPF_PROG(deny_net, int family, int type, int protocol, int kern, int ret)
{
	__u64 cg;

	if (ret != 0)
		return ret;              /* до нас уже відмовили — не сперечаємось */
	if (kern)
		return 0;                /* сокет заводить саме ядро, не процес */
	if (family == AF_UNIX)
		return 0;

	cg = bpf_get_current_cgroup_id();
	if (!bpf_map_lookup_elem(&caged, &cg))
		return 0;

	return -EPERM;
}
