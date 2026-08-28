#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>

/* ЗАСТАРІЛА / ОГОЛОШЕНА НЕБЕЗПЕЧНОЮ (POSIX.1-2008 Deprecated) */
struct hostent *gethostbyname(const char *name);

/* СУЧАСНИЙ РЕЕНТРАБЕЛЬНИЙ ТА ПОТОКОБЕЗПЕЧНИЙ СТАНДАРТ */
int getaddrinfo(const char *node, const char *service,
                const struct addrinfo *hints,
                struct addrinfo **res);

void freeaddrinfo(struct addrinfo *res);

int getnameinfo(const struct sockaddr *addr, socklen_t addrlen,
                char *host, socklen_t hostlen,
                char *serv, socklen_t servlen, int flags);
