/* Спрощена концептуальна схема структур ядра з net/tls */
struct tls_sw_context_tx {
    struct crypto_aead *aead_send;  /* Хендл симетричного шифру з Crypto API */
    struct scatterlist sg_tx_data[MAX_SKB_FRAGS]; /* SG-список незашифрованих сторінок */
    u64 rec_seq;                    /* 64-бітний порядковий номер запису TLS TX */
    char iv[TLS_CIPHER_AES_GCM_128_IV_SIZE];
    char rec_seq_size;
};

struct tls_context {
    struct sock *sk;
    enum tls_offload_mode tx_conf;  /* TLS_SW або TLS_HW */
    enum tls_offload_mode rx_conf;
    void *priv_ctx_tx;              /* Вказує на struct tls_sw_context_tx */
    void *priv_ctx_rx;
};
