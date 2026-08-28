#include <stdio.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int main(void) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in addr = {0};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(9099);
    inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

    connect(fd, (struct sockaddr*)&addr, sizeof(addr));

    send(fd, "hello ", 6, 0);
    usleep(100000); // 100мс затримка

    // Відправлення позасмугового байта
    send(fd, "!", 1, MSG_OOB);
    usleep(100000);

    send(fd, "world\n", 6, 0);

    close(fd);
    return 0;
}
