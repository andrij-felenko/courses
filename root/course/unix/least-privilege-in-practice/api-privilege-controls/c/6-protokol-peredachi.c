#include <sys/socket.h>
#include <sys/un.h>

struct msghdr {
    void         *msg_name;       /* Адреса сокета (NULL для підключених потокових сокетів) */
    socklen_t     msg_namelen;    /* Розмір адреси */
    struct iovec *msg_iov;        /* Масив буферів корисних даних */
    size_t        msg_iovlen;     /* Кількість буферів у масиві msg_iov */
    void         *msg_control;    /* Буфер допоміжних службових повідомлень */
    size_t        msg_controllen; /* Розмір буфера msg_control */
    int           msg_flags;      /* Прапорці отриманого повідомлення */
};

struct cmsghdr {
    size_t cmsg_len;   /* Розмір службового блоку разом із заголовком */
    int    cmsg_level; /* SOL_SOCKET */
    int    cmsg_type;  /* SCM_RIGHTS */
    /* unsigned char cmsg_data[] — масив дескрипторів слідує безпосередньо за структурою */
};
