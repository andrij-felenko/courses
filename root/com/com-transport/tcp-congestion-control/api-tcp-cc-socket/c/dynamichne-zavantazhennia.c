/* Приклад eBPF-програми для кастомного контролера заторів */
SEC("struct_ops")
void BPF_PROG(bpf_custom_cong_avoid, struct sock *sk, u32 ack, u32 acked)
{
    struct tcp_sock *tp = tcp_sk(sk);
    if (!tcp_is_cwnd_limited(sk))
        return;

    if (tcp_in_slow_start(tp)) {
        acked = tcp_slow_start(tp, acked);
        if (!acked)
            return;
    }
    /* Кастомне лінійне розширення вікна */
    tcp_cong_avoid_ai(tp, tp->snd_cwnd, acked);
}

SEC(".struct_ops")
struct tcp_congestion_ops bpf_custom_ops = {
    .cong_avoid = (void *)bpf_custom_cong_avoid,
    .name       = "bpf_custom",
};
