#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_endian.h>

/* Оголошення BPF-карти сокетів типу SOCKMAP з 2 елементами */
struct {
    __uint(type, BPF_MAP_TYPE_SOCKMAP);
    __uint(max_entries, 2);
    __type(key, __u32);
    __type(value, __u32);
} sock_map SEC(".maps");

/* BPF_PROG_TYPE_SK_MSG програма вердикту, яка викликається при sendmsg */
SEC("sk_msg")
int bpf_sockmap_redirect(struct sk_msg_md *msg)
{
    /* Ключ 0 відповідає Сокету A (Proxy), ключ 1 — Сокету B (Backend).
     * Якщо дані надходять від сокета 0, спрямовуємо їх на сокет 1.
     * Прапор BPF_F_INGRESS розміщує байти безпосередньо у чергу прийому Sock B.
     */
    __u32 target_key = 1;

    /* Перенаправляємо вектор сторінок у сокет з ключем 1 */
    return bpf_msg_redirect_map(msg, &sock_map, target_key, BPF_F_INGRESS);
}

char _license[] SEC("license") = "GPL";
