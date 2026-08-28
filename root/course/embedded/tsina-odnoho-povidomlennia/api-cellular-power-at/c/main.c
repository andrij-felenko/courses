#include <zephyr/net/socket.h>

/* Відправка UDP-датаграми з миттєвим скиданням RRC-з'єднання */
ssize_t sent = sendto(
    sock_fd,
    frame_buffer,
    frame_len,
    MSG_DONTWAIT | RAI_FLAG_NO_REPLY, /* Прапорець швидкого виходу в сон */
    (struct sockaddr *)&dest_addr,
    sizeof(dest_addr)
);
