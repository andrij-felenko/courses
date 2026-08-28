struct xfrm_state {
    possible_net_t          xs_net;
    union {
        struct hlist_node   gstate_node;
        struct hlist_node   state_hlist;
    };
    struct xfrm_id          id;         /* Dst IP, SPI, Proto */
    struct xfrm_selector    sel;        /* Селектор прив'язки */
    xfrm_address_t          saddr;      /* Src IP */
    
    struct xfrm_lifetime_cfg lft;
    struct xfrm_lifetime_cur curlft;
    struct xfrm_stats       stats;

    /* Криптографічні трансформатори Crypto API */
    struct crypto_aead     *aead;       /* Алгоритм AEAD (наприклад, AES-GCM) */
    struct crypto_ahash    *aalg;       /* Алгоритм HMAC */
    struct crypto_skcipher *ealg;       /* Алгоритм блочного шифрування */

    const struct xfrm_mode *inner_mode; /* Внутрішній режим обробки */
    const struct xfrm_mode *outer_mode; /* Зовнішній режим обробки */

    u32                     reqid;      /* Ідентифікатор зв'язку з SP */
    u32                     seq;        /* Лічильник послідовності пакета */
    struct xfrm_replay_state replay;    /* Стан захисту від повторів */
};
