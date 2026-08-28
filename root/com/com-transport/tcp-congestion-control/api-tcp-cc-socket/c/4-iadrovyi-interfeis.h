struct tcp_congestion_ops {
    struct list_head list;
    char name[TCP_CA_NAME_MAX];

    /* Ініціалізація та знищення стану сокета */
    void (*init)(struct sock *sk);
    void (*release)(struct sock *sk);

    /* Обчислення ssthresh при виявленні втрати */
    u32  (*ssthresh)(struct sock *sk);

    /* Основний крок зростання cwnd при отриманні ACK */
    void (*cong_avoid)(struct sock *sk, u32 ack, u32 acked);

    /* Зміна стану кінцевого автомата (Open, Disorder, Recovery, Loss) */
    void (*set_state)(struct sock *sk, u8 new_state);

    /* Реагування на скасування помилкових втрат (DSACK) */
    u32  (*undo_cwnd)(struct sock *sk);

    /* Обробка підтверджених пакетів (для BBR / pacing) */
    void (*pkts_acked)(struct sock *sk, const struct ack_sample *sample);

    /* Обчислення швидкості пейсингу */
    void (*cong_control)(struct sock *sk, const struct rate_sample *rs);

    struct module *owner;
};
