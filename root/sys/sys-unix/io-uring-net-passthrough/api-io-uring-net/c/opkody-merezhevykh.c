/* c */
enum io_uring_op {
    IORING_OP_SEND          = 26,   /* Стандартне копіювальне відправлення */
    IORING_OP_RECV          = 27,   /* Стандартне копіювальне отримання */
    IORING_OP_ACCEPT        = 28,   /* Прийняття нових TCP-з'єднань */
    IORING_OP_CONNECT       = 31,   /* Ініціалізація вихідного TCP-з'єднання */
    IORING_OP_SEND_ZC       = 38,   /* Zero-Copy відправлення даних (Linux 6.0+) */
    IORING_OP_RECV_ZC       = 52,   /* Zero-Copy отримання даних (Linux 6.7+) */
    IORING_OP_URING_CMD     = 46,   /* Passthrough команди до сокетів/пристроїв */
};
