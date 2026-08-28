struct xfrm_lifetime_cfg {
    __u64 soft_byte_limit;   /* М'який ліміт оброблених байтів */
    __u64 hard_byte_limit;   /* Жорсткий ліміт оброблених байтів */
    __u64 soft_packet_limit; /* М'який ліміт оброблених пакетів */
    __u64 hard_packet_limit; /* Жорсткий ліміт оброблених пакетів */
    __u64 soft_add_expires_seconds;  /* М'який ліміт часу від моменту створення */
    __u64 hard_add_expires_seconds;  /* Жорсткий ліміт часу від моменту створення */
    __u64 soft_use_expires_seconds;  /* М'який ліміт часу від першого використання */
    __u64 hard_use_expires_seconds;  /* Жорсткий ліміт часу від першого використання */
};
