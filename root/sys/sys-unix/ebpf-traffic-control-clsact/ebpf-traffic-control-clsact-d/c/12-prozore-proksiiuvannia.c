SEC("classifier")
int tc_tproxy(struct __sk_buff *skb) {
    // ... розпарсування L2-L4 ...

    struct bpf_sock_tuple tuple = {};
    tuple.ipv4.saddr = ip->saddr;
    tuple.ipv4.daddr = ip->daddr;
    tuple.ipv4.sport = tcp->source;
    tuple.ipv4.dport = tcp->dest;

    // 1. Пошук локального listening-сокета Envoy у сокетній таблиці ядра
    struct bpf_sock *sk = bpf_skc_lookup_tcp(skb, &tuple, sizeof(tuple.ipv4), BPF_F_CURRENT_NETNS, 0);
    if (sk) {
        if (sk->state == BPF_TCP_LISTEN) {
            // 2. Пряме призначення сокета сокетному буферу skb
            if (bpf_sk_assign(skb, sk, 0) == 0) {
                bpf_sk_release(sk);
                return TC_ACT_OK; // Пакет іде прямо у сокет Envoy без routing!
            }
        }
        bpf_sk_release(sk);
    }
    return TC_ACT_OK;
}
