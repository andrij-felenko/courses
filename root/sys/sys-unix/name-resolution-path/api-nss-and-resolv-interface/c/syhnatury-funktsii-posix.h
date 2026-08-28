int getaddrinfo(
    const char *node,
    const char *service,
    const struct addrinfo *hints,
    struct addrinfo **res
);

void freeaddrinfo(struct addrinfo *res);

const char *gai_strerror(int errcode);

int getnameinfo(
    const struct sockaddr *sa,
    socklen_t salen,
    char *host,
    size_t hostlen,
    char *serv,
    size_t servlen,
    int flags
);
