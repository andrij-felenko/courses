#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <openssl/x509v3.h>

int main(void) {
    SSL_library_init();
    OpenSSL_add_all_algorithms();
    SSL_load_error_strings();

    SSL_CTX *ctx = SSL_CTX_new(TLS_client_method());
    if (!ctx) {
        fprintf(stderr, "Помилка створення SSL_CTX\n");
        return 1;
    }

    /* Вмикаємо перевірку сервера та завантажуємо CA бандл */
    SSL_CTX_set_verify(ctx, SSL_VERIFY_PEER, NULL);
    if (!SSL_CTX_load_verify_locations(ctx, "ca.crt", NULL)) {
        fprintf(stderr, "Помилка завантаження ca.crt\n");
        SSL_CTX_free(ctx);
        return 1;
    }

    /* Завантажуємо клієнтський сертифікат та приватний ключ для mTLS */
    if (SSL_CTX_use_certificate_chain_file(ctx, "client.crt") <= 0 ||
        SSL_CTX_use_PrivateKey_file(ctx, "client.key", SSL_FILETYPE_PEM) <= 0 ||
        !SSL_CTX_check_private_key(ctx)) {
        fprintf(stderr, "Помилка завантаження клієнтського сертифіката чи ключа\n");
        SSL_CTX_free(ctx);
        return 1;
    }

    /* Встановлюємо перевірку імені хоста в SAN */
    X509_VERIFY_PARAM *param = SSL_CTX_get0_param(ctx);
    X509_VERIFY_PARAM_set1_host(param, "localhost", 0);

    /* Створення TCP-з'єднання */
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(8443);
    inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

    if (connect(sock, (struct sockaddr *)&addr, sizeof(addr)) != 0) {
        perror("Помилка підключення TCP");
        close(sock);
        SSL_CTX_free(ctx);
        return 1;
    }

    SSL *ssl = SSL_new(ctx);
    SSL_set_fd(ssl, sock);
    SSL_set_tlsext_host_name(ssl, "localhost");

    if (SSL_connect(ssl) <= 0) {
        fprintf(stderr, "Помилка TLS Handshake: %s\n",
                ERR_error_string(ERR_get_error(), NULL));
        SSL_free(ssl);
        close(sock);
        SSL_CTX_free(ctx);
        return 1;
    }

    printf("TLS-з'єднання встановлено з шифром: %s\n", SSL_get_cipher(ssl));

    const char *http_req = "GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n";
    SSL_write(ssl, http_req, (int)strlen(http_req));

    char buf[512];
    int bytes = SSL_read(ssl, buf, sizeof(buf) - 1);
    if (bytes > 0) {
        buf[bytes] = '\0';
        printf("Отримано відповідь:\n%s\n", buf);
    }

    SSL_shutdown(ssl);
    SSL_free(ssl);
    close(sock);
    SSL_CTX_free(ctx);
    return 0;
}
