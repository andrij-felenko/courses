#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <openssl/x509v3.h>

/* Створення та суворе налаштування клієнтського SSL_CTX */
SSL_CTX *create_secure_client_ctx(const char *ca_file, const char *client_cert, const char *client_key) {
    const SSL_METHOD *method = TLS_client_method();
    SSL_CTX *ctx = SSL_CTX_new(method);
    if (!ctx) {
        fprintf(stderr, "Помилка виділення пам'яті під SSL_CTX\n");
        return NULL;
    }

    /* Вимагаємо обов'язкову верифікацію сертифіката сервера */
    SSL_CTX_set_verify(ctx, SSL_VERIFY_PEER, NULL);

    /* Завантажуємо довірені кореневі/проміжні сертифікати */
    if (SSL_CTX_load_verify_locations(ctx, ca_file, NULL) != 1) {
        fprintf(stderr, "Помилка завантаження CA файлу: %s\n", ca_file);
        SSL_CTX_free(ctx);
        return NULL;
    }

    /* Забороняємо застарілі та небезпечні протоколи */
    SSL_CTX_set_min_proto_version(ctx, TLS1_2_VERSION);

    /* Якщо вказано — завантажуємо клієнтський сертифікат і ключ для mTLS */
    if (client_cert && client_key) {
        if (SSL_CTX_use_certificate_chain_file(ctx, client_cert) <= 0 ||
            SSL_CTX_use_PrivateKey_file(ctx, client_key, SSL_FILETYPE_PEM) <= 0 ||
            !SSL_CTX_check_private_key(ctx)) {
            fprintf(stderr, "Помилка перевірки клієнтського сертифіката/ключа mTLS\n");
            SSL_CTX_free(ctx);
            return NULL;
        }
    }

    return ctx;
}

int send_secure_request(SSL_CTX *ctx, const char *hostname, int port) {
    /* Вмикаємо перевірку імені хоста за RFC 6125 у структурі параметрів */
    X509_VERIFY_PARAM *param = SSL_CTX_get0_param(ctx);
    X509_VERIFY_PARAM_set_hostflags(param, X509_CHECK_FLAG_NO_PARTIAL_WILDCARDS);
    if (X509_VERIFY_PARAM_set1_host(param, hostname, 0) != 1) {
        fprintf(stderr, "Помилка встановлення імені для перевірки SAN\n");
        return -1;
    }

    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) return -1;

    struct hostent *he = gethostbyname(hostname);
    if (!he) { close(sock); return -1; }

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    memcpy(&server_addr.sin_addr.s_addr, he->h_addr_list[0], he->h_length);

    if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) != 0) {
        perror("TCP Connect failed");
        close(sock);
        return -1;
    }

    SSL *ssl = SSL_new(ctx);
    SSL_set_fd(ssl, sock);
    /* Встановлюємо розширення SNI (Server Name Indication) */
    SSL_set_tlsext_host_name(ssl, hostname);

    if (SSL_connect(ssl) <= 0) {
        long verify_err = SSL_get_verify_result(ssl);
        fprintf(stderr, "Помилка TLS рукостискання: %s (Код валідації: %ld - %s)\n",
                ERR_error_string(ERR_get_error(), NULL),
                verify_err, X509_verify_cert_error_string(verify_err));
        SSL_free(ssl);
        close(sock);
        return -1;
    }

    printf("TLS успішно встановлено з %s. Шифр: %s\n", hostname, SSL_get_cipher(ssl));

    const char req[] = "GET /v1/status HTTP/1.1\r\nHost: api.internal.corp\r\nConnection: close\r\n\r\n";
    SSL_write(ssl, req, (int)strlen(req));

    char buf[512];
    int read_bytes = SSL_read(ssl, buf, sizeof(buf) - 1);
    if (read_bytes > 0) {
        buf[read_bytes] = '\0';
        printf("Отримано відповідь:\n%s\n", buf);
    }

    SSL_shutdown(ssl);
    SSL_free(ssl);
    close(sock);
    return 0;
}
