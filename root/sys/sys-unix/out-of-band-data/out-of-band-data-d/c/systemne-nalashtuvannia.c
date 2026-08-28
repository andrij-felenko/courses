/* Обчислення urg_seq у ядрі Linux */
static void tcp_urg(struct sock *sk, struct sk_buff *skb, const struct tcphdr *th)
{
    struct tcp_sock *tp = tcp_sk(sk);
    u32 ptr = ntohs(th->urg_ptr);

    if (ptr && !sock_net(sk)->ipv4.sysctl_tcp_stdurg)
        ptr--; // Зсув на 1 байт для режиму BSD (tcp_stdurg=0)

    tp->urg_seq = TCP_SKB_CB(skb)->seq + ptr;
    tp->urg_data = TCP_URG_VALID;
}
