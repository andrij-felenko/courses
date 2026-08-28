struct sock {
    struct sock_common    __sk_common;  /* Мережевий ідентифікатор: IP-адреси, порти, протокол, хеш-ключі */
    unsigned char         sk_shutdown;  /* Прапорці припинення передачі (RCV_SHUTDOWN, SEND_SHUTDOWN) */
    unsigned short        sk_type;      /* Тип сокета */
    int                   sk_rcvbuf;    /* Поточний розмір буфера прийому у байтах */
    int                   sk_sndbuf;    /* Поточний розмір буфера передачі у байтах */
    struct sk_buff_head   sk_receive_queue; /* Двобічний список накопичених мережевих буферів sk_buff */
    struct sk_buff_head   sk_write_queue;   /* Двобічний список вихідних буферів sk_buff */
    struct socket        *sk_socket;    /* Зворотний вказівник на верхній шар struct socket */
    struct proto         *sk_prot;      /* Таблиця протокольних функцій (tcp_prot, udp_prot) */
    void                (*sk_data_ready)(struct sock *sk); /* Зворотний виклик розбудження процесів при надходженні даних */
};
