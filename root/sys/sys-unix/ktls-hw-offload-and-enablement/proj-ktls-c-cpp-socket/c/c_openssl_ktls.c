/* c_openssl_ktls.c - Використання OpenSSL 3.0 з kTLS на мові C */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/sendfile.h>
#include <openssl/ssl.h>
#include <openssl/err.h>

/*
 * Налаштування контексту OpenSSL для автоматичного використання kTLS
 */
void setup_openssl_ktls_ctx(SSL_CTX *ctx) {
    /* Дозволяємо OpenSSL автоматично передавати ключі у ядро Linux */
    SSL_CTX_set_options(ctx, SSL_OP_ENABLE_KTLS);
}

/*
 * Обслуговування клієнтського запиту: якщо kTLS активний, робимо sendfile(),
 * інакше використовуємо класичний цикл SSL_write().
 */
int serve_file_via_ktls(SSL *ssl, int sock_fd, int file_fd, size_t file_size) {
    BIO *wbio = SSL_get_wbio(ssl);

    /* Перевіряємо, чи ядро підхопило kTLS для вихідного напрямку TX */
    if (wbio != NULL && BIO_get_ktls_send(wbio)) {
        printf("[OpenSSL Integration] kTLS увімкнено! Використовуємо Zero-Copy sendfile()\n");
        off_t offset = 0;
        ssize_t sent = sendfile(sock_fd, file_fd, &offset, file_size);
        if (sent < 0) {
            perror("Помилка sendfile у режимі kTLS");
            return -1;
        }
        printf("[OpenSSL Integration] Успішно передано %zd байт через kTLS sendfile()\n", sent);
        return 0;
    }

    /* Фолбек для систем без підтримки kTLS: класичний Userspace шифрувальний цикл */
    printf("[OpenSSL Integration] kTLS недоступний. Використовуємо стандартне шифрування SSL_write()\n");
    char buffer[8192];
    ssize_t bytes_read;
    while ((bytes_read = read(file_fd, buffer, sizeof(buffer))) > 0) {
        int written = SSL_write(ssl, buffer, (int)bytes_read);
        if (written <= 0) {
            ERR_print_errors_fp(stderr);
            return -1;
        }
    }
    return 0;
}
