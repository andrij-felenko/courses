/* Концептуальна схема зв'язку об'єктів сокета у ядрі */
struct file {
    const struct file_operations *f_op; /* Вказує на socket_file_ops */
    void *private_data;                  /* Вказує на struct socket */
};

struct socket {
    socket_state state;                 /* SS_UNCONNECTED, SS_CONNECTED */
    struct file *file;                  /* Зворотний вказівник на struct file */
    struct sock *sk;                    /* Вказівник на мережевий struct sock */
    const struct proto_ops *ops;        /* inet_stream_ops / inet_dgram_ops */
};

struct sock {
    struct sock_common __sk_common;     /* Адреси, порти, протокол */
    struct socket *sk_socket;           /* Зворотний вказівник на struct socket */
    struct sk_buff_head sk_receive_queue;/* Черга вхідних кадрів */
    struct sk_buff_head sk_write_queue;  /* Черга вихідних кадрів */
};
