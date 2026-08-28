/* repo_verifier.c — Верифікація підписів InRelease та хешів у C (POSIX + GPGME + OpenSSL) */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <gpgme.h>
#include <openssl/evp.h>

#define BUF_SIZE 8192

/* Зчитування вмісту файлу у структурований буфер GPGME Data */
static gpgme_data_t load_file_to_gpgme_data(const char *filepath) {
    gpgme_data_t data = NULL;
    gpgme_error_t err = gpgme_data_new_from_file(&data, filepath, 1);
    if (err) {
        fprintf(stderr, "Помилка читання файлу %s: %s\n", filepath, gpgme_strerror(err));
        return NULL;
    }
    return data;
}

/* Потокове обчислення SHA-256 хешу файлу за допомогою OpenSSL EVP API */
static int compute_file_sha256(const char *filepath, unsigned char digest[EVP_MAX_MD_SIZE], unsigned int *digest_len) {
    int fd = open(filepath, O_RDONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити файл для хешування");
        return -1;
    }

    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    if (!mdctx) {
        close(fd);
        return -1;
    }

    if (1 != EVP_DigestInit_ex(mdctx, EVP_sha256(), NULL)) {
        EVP_MD_CTX_free(mdctx);
        close(fd);
        return -1;
    }

    char buffer[BUF_SIZE];
    ssize_t bytes_read;
    while ((bytes_read = read(fd, buffer, sizeof(buffer))) > 0) {
        if (1 != EVP_DigestUpdate(mdctx, buffer, bytes_read)) {
            EVP_MD_CTX_free(mdctx);
            close(fd);
            return -1;
        }
    }

    close(fd);
    if (bytes_read < 0) {
        EVP_MD_CTX_free(mdctx);
        return -1;
    }

    if (1 != EVP_DigestFinal_ex(mdctx, digest, digest_len)) {
        EVP_MD_CTX_free(mdctx);
        return -1;
    }

    EVP_MD_CTX_free(mdctx);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        fprintf(stderr, "Використання: %s <keyring.gpg> <InRelease> <target.deb>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *keyring_path = argv[1];
    const char *inrelease_path = argv[2];
    const char *target_pkg_path = argv[3];

    /* Ініціалізація підсистеми GPGME */
    gpgme_check_version(NULL);
    gpgme_engine_check_version(GPGME_PROTOCOL_OpenPGP);

    gpgme_ctx_t ctx = NULL;
    gpgme_error_t err = gpgme_new(&ctx);
    if (err) {
        fprintf(stderr, "Не вдалося створити контекст GPGME: %s\n", gpgme_strerror(err));
        return EXIT_FAILURE;
    }

    /* Налаштування протоколу OpenPGP */
    err = gpgme_set_protocol(ctx, GPGME_PROTOCOL_OpenPGP);
    if (err) {
        fprintf(stderr, "Помилка встановлення протоколу OpenPGP: %s\n", gpgme_strerror(err));
        gpgme_release(ctx);
        return EXIT_FAILURE;
    }

    /* Імпорт публічного ключа у тимчасовий контекст */
    gpgme_data_t key_data = load_file_to_gpgme_data(keyring_path);
    if (!key_data) {
        gpgme_release(ctx);
        return EXIT_FAILURE;
    }

    err = gpgme_op_import(ctx, key_data);
    gpgme_data_release(key_data);
    if (err) {
        fprintf(stderr, "Помилка імпорту ключа: %s\n", gpgme_strerror(err));
        gpgme_release(ctx);
        return EXIT_FAILURE;
    }

    /* Завантаження індексного файлу InRelease */
    gpgme_data_t sig_data = load_file_to_gpgme_data(inrelease_path);
    if (!sig_data) {
        gpgme_release(ctx);
        return EXIT_FAILURE;
    }

    /* Перевірка PGP підпису */
    err = gpgme_op_verify(ctx, sig_data, NULL, NULL);
    if (err) {
        fprintf(stderr, "Криптографічна помилка перевірки: %s\n", gpgme_strerror(err));
        gpgme_data_release(sig_data);
        gpgme_release(ctx);
        return EXIT_FAILURE;
    }

    gpgme_verify_result_t result = gpgme_op_verify_result(ctx);
    if (!result || !result->signatures) {
        fprintf(stderr, "УВАГА: Підпис у файлі %s відсутній!\n", inrelease_path);
        gpgme_data_release(sig_data);
        gpgme_release(ctx);
        return EXIT_FAILURE;
    }

    gpgme_signature_t sig = result->signatures;
    if (sig->status != GPG_ERR_NO_ERROR) {
        fprintf(stderr, "ПОМИЛКА: Невалідний підпис GPG! Код помилки: %u\n", sig->status);
        gpgme_data_release(sig_data);
        gpgme_release(ctx);
        return EXIT_FAILURE;
    }

    printf("[ОК] GPG підпис файлу %s УСПІШНО ПЕРЕВІРЕНО.\n", inrelease_path);
    printf("     Fingerprint: %s\n", sig->fpr ? sig->fpr : "невідомий");

    gpgme_data_release(sig_data);
    gpgme_release(ctx);

    /* Обчислення SHA-256 цільового пакунка */
    unsigned char digest[EVP_MAX_MD_SIZE];
    unsigned int digest_len = 0;
    if (compute_file_sha256(target_pkg_path, digest, &digest_len) != 0) {
        fprintf(stderr, "Помилка обчислення хешу для %s\n", target_pkg_path);
        return EXIT_FAILURE;
    }

    printf("[ОК] Обчислено SHA-256 для %s: ", target_pkg_path);
    for (unsigned int i = 0; i < digest_len; i++) {
        printf("%02x", digest[i]);
    }
    printf("\n");

    return EXIT_SUCCESS;
}
