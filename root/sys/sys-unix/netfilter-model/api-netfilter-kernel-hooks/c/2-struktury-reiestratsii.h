struct nf_hook_state {
    unsigned int        hook;      /* Номер поточного хука (enum nf_inet_hooks) */
    u_int8_t            pf;        /* Родина протоколів (NFPROTO_IPV4, NFPROTO_IPV6 тощо) */
    struct net_device  *in;        /* Вхідний мережевий інтерфейс (або NULL) */
    struct net_device  *out;       /* Вихідний мережевий інтерфейс (або NULL) */
    struct sock        *sk;        /* Пов'язаний сокет (якщо є для LOCAL_IN/LOCAL_OUT) */
    struct net         *net;       /* Мережевий простір назв (Network Namespace) */
    int                (*okfn)(struct net *, struct sock *, struct sk_buff *);
                                   /* Функція продовження стека при поверненні NF_ACCEPT */
};

typedef unsigned int nf_hookfn(void *priv,
                               struct sk_buff *skb,
                               const struct nf_hook_state *state);

struct nf_hook_ops {
    nf_hookfn           *hook;     /* Вказівник на функцію зворотного виклику */
    struct net_device   *dev;      /* Обмеження конкретним пристроєм (опціонально) */
    void                *priv;     /* Приватні дані користувача, що передаються в hook() */
    u_int8_t            pf;        /* Родина протоколів (наприклад, NFPROTO_IPV4) */
    enum nf_inet_hooks  hooknum;   /* Точка перехоплення (наприклад, NF_INET_PRE_ROUTING) */
    int                 priority;  /* Числовий пріоритет виконання (менше значення = раніше) */
};
