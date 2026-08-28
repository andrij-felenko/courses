struct addrinfo {
    int              ai_flags;      /* Прапорці поведінки (AI_PASSIVE, AI_CANONNAME тощо) */
    int              ai_family;     /* Сімейство адрес: AF_INET, AF_INET6, AF_UNSPEC */
    int              ai_socktype;   /* Тип сокета: SOCK_STREAM, SOCK_DGRAM */
    int              ai_protocol;   /* Протокол: IPPROTO_TCP, IPPROTO_UDP, 0 */
    socklen_t        ai_addrlen;    /* Довжина сокетної адреси у байтах */
    struct sockaddr *ai_addr;       /* Вказівник на структуру sockaddr_in або sockaddr_in6 */
    char            *ai_canonname;  /* Канонічне ім'я хоста (якщо вказано AI_CANONNAME) */
    struct addrinfo *ai_next;       /* Вказівник на наступний елемент зв'язаного списку */
};
