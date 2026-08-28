/* C11 implementation: TLS 1.3 Client connection using OpenSSL */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <sys/socket.h>

#include <openssl/ssl.h>
#include <openssl/err.h>

#define HOST "example.com"
#define PORT "443"

static int create_socket(const char *hostname, const char *port_str) {
    struct addrinfo hints, *res, *p;
    int fd = -1;

    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    if (getaddrinfo(hostname, port_str, &hints, &res) != 0) {
        perror("getaddrinfo failed");
        return -1;
    }

    for (p = res; p != NULL; p = p->ai_next) {
        fd = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
        if (fd < 0) continue;
        if (connect(fd, p->ai_addr, p->ai_addrlen) == 0) break;
        close(fd);
        fd = -1;
    }

    freeaddrinfo(res);
    return fd;
}

int main(void) {
    SSL_library_init();
    SSL_load_error_strings();
    OpenSSL_add_all_algorithms();

    /* Створення контексту TLS */
    SSL_CTX *ctx = SSL_CTX_new(TLS_client_method());
    if (!ctx) {
        fprintf(stderr, "Unable to create SSL context\n");
        ERR_print_errors_fp(stderr);
        return EXIT_FAILURE;
    }

    /* Примусово вимагаємо TLS 1.3 як мінімальну та максимальну версію */
    if (!SSL_CTX_set_min_proto_version(ctx, TLS1_3_VERSION) ||
        !SSL_CTX_set_max_proto_version(ctx, TLS1_3_VERSION)) {
        fprintf(stderr, "Failed to enforce TLS 1.3 protocol version\n");
        SSL_CTX_free(ctx);
        return EXIT_FAILURE;
    }

    /* Завантаження системних довірених кореневих сертифікатів CA */
    if (!SSL_CTX_set_default_verify_paths(ctx)) {
        fprintf(stderr, "Failed to load default CA paths\n");
    }

    int sock = create_socket(HOST, PORT);
    if (sock < 0) {
        fprintf(stderr, "Failed to connect to %s:%s\n", HOST, PORT);
        SSL_CTX_free(ctx);
        return EXIT_FAILURE;
    }

    SSL *ssl = SSL_new(ctx);
    SSL_set_fd(ssl, sock);

    /* Обов'язково додаємо SNI (Server Name Indication) */
    SSL_set_tlsext_host_name(ssl, HOST);
    /* Налаштування перевірки відповідності імені хоста у сертифікаті */
    SSL_set1_host(ssl, HOST);
    SSL_set_verify(ssl, SSL_VERIFY_PEER, NULL);

    printf("Initiating TLS 1.3 Handshake with %s...\n", HOST);
    if (SSL_connect(ssl) <= 0) {
        fprintf(stderr, "TLS Handshake failed!\n");
        ERR_print_errors_fp(stderr);
        SSL_free(ssl);
        close(sock);
        SSL_CTX_free(ctx);
        return EXIT_FAILURE;
    }

    printf("Handshake successful!\n");
    printf("Protocol version: %s\n", SSL_get_version(ssl));
    printf("Negotiated Cipher Suite: %s\n", SSL_get_cipher(ssl));

    /* Відправка HTTP GET запиту через захищений канал */
    const char *http_request = "GET / HTTP/1.1\r\nHost: " HOST "\r\nConnection: close\r\n\r\n";
    SSL_write(ssl, http_request, (int)strlen(http_request));

    char buf[512];
    int bytes = SSL_read(ssl, buf, sizeof(buf) - 1);
    if (bytes > 0) {
        buf[bytes] = '\0';
        printf("\nReceived Response Header:\n%.150s...\n", buf);
    }

    /* Охайне закриття з'єднання (send close_notify alert) */
    SSL_shutdown(ssl);
    SSL_free(ssl);
    close(sock);
    SSL_CTX_free(ctx);

    return EXIT_SUCCESS;
}
