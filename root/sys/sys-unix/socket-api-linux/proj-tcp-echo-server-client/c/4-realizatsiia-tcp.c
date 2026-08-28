#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define SERVER_IP "127.0.0.1"
#define PORT 8080
#define MESSAGE "Hello, Linux Socket API!"

int main(void) {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("socket failed");
        return EXIT_FAILURE;
    }

    struct sockaddr_in serv_addr;
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);

    if (inet_pton(AF_INET, SERVER_IP, &serv_addr.sin_addr) <= 0) {
        perror("inet_pton invalid address");
        close(sockfd);
        return EXIT_FAILURE;
    }

    if (connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        perror("connect failed");
        close(sockfd);
        return EXIT_FAILURE;
    }

    printf("Connected to server %s:%d\n", SERVER_IP, PORT);

    ssize_t sent = write(sockfd, MESSAGE, strlen(MESSAGE));
    if (sent < 0) {
        perror("write failed");
        close(sockfd);
        return EXIT_FAILURE;
    }

    char response[1024];
    ssize_t received = read(sockfd, response, sizeof(response) - 1);
    if (received > 0) {
        response[received] = '\0';
        printf("Received echo: %s\n", response);
    }

    close(sockfd);
    return EXIT_SUCCESS;
}
