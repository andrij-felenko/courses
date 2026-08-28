int  bind(int fd, const struct sockaddr *addr, socklen_t len);
int  listen(int fd, int backlog);
int  accept(int fd, struct sockaddr *addr, socklen_t *len);
int  connect(int fd, const struct sockaddr *addr, socklen_t len);

ssize_t send(int fd, const void *buf, size_t n, int flags);
ssize_t recv(int fd, void *buf, size_t n, int flags);
ssize_t sendto(int fd, const void *buf, size_t n, int flags,
               const struct sockaddr *dst, socklen_t dstlen);
ssize_t recvfrom(int fd, void *buf, size_t n, int flags,
                 struct sockaddr *src, socklen_t *srclen);
