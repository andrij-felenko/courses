#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <openssl/bio.h>
#include <openssl/x509.h>
#include <openssl/pem.h>
#include <openssl/evp.h>

#define MAX_PATH 512
#define BUFFER_SIZE 8192

/* Читання бінарного файла із sysfs у динамічно виділений буфер */
static unsigned char *read_sysfs_file(const char *path, size_t *out_len) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        perror("Failed to open sysfs attribute file");
        return NULL;
    }

    unsigned char *buf = malloc(BUFFER_SIZE);
    if (!buf) {
        close(fd);
        return NULL;
    }

    ssize_t bytes_read = read(fd, buf, BUFFER_SIZE);
    close(fd);

    if (bytes_read <= 0) {
        free(buf);
        return NULL;
    }

    *out_len = (size_t)bytes_read;
    return buf;
}

/* Перевірка підпису ECDSA над дайджестом вимірювання SPDM */
int verify_spdm_measurement(const char *sysfs_dir) {
    char cert_path[MAX_PATH];
    char meas_path[MAX_PATH];
    unsigned char *cert_buf = NULL;
    unsigned char *meas_buf = NULL;
    size_t cert_len = 0, meas_len = 0;
    int result = -1;

    snprintf(cert_path, sizeof(cert_path), "%s/certificates/slot0", sysfs_dir);
    snprintf(meas_path, sizeof(meas_path), "%s/measurements/raw", sysfs_dir);

    cert_buf = read_sysfs_file(cert_path, &cert_len);
    meas_buf = read_sysfs_file(meas_path, &meas_len);

    if (!cert_buf || !meas_buf) {
        fprintf(stderr, "Error: Missing SPDM certificates or measurements in sysfs.\n");
        goto cleanup;
    }

    /* Декодування DER-сертифіката X.509 */
    const unsigned char *p = cert_buf;
    X509 *cert = d2i_X509(NULL, &p, cert_len);
    if (!cert) {
        fprintf(stderr, "Error: Failed to parse X.509 DER certificate.\n");
        goto cleanup;
    }

    /* Вилучення публічного ключа зі структури сертифіката */
    EVP_PKEY *pubkey = X509_get0_pubkey(cert);
    if (!pubkey) {
        fprintf(stderr, "Error: Failed to extract public key from certificate.\n");
        X509_free(cert);
        goto cleanup;
    }

    /* Створення контексту перевірки підпису EVP_MD_CTX */
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    if (!ctx) {
        X509_free(cert);
        goto cleanup;
    }

    /* Налаштування перевірки ECDSA підпису з хешем SHA-384 */
    if (EVP_DigestVerifyInit(ctx, NULL, EVP_sha384(), NULL, pubkey) <= 0) {
        fprintf(stderr, "Error initializing DigestVerify context.\n");
        EVP_MD_CTX_free(ctx);
        X509_free(cert);
        goto cleanup;
    }

    /* meas_buf містить: [Data_Block (meas_len - 96)] [Signature (96 bytes)] */
    size_t sig_len = 96;
    if (meas_len <= sig_len) {
        fprintf(stderr, "Error: Measurement buffer too small for signature.\n");
        EVP_MD_CTX_free(ctx);
        X509_free(cert);
        goto cleanup;
    }

    size_t data_len = meas_len - sig_len;
    unsigned char *data_ptr = meas_buf;
    unsigned char *sig_ptr = meas_buf + data_len;

    if (EVP_DigestVerifyUpdate(ctx, data_ptr, data_len) <= 0) {
        fprintf(stderr, "Error in DigestVerifyUpdate.\n");
        EVP_MD_CTX_free(ctx);
        X509_free(cert);
        goto cleanup;
    }

    int rc = EVP_DigestVerifyFinal(ctx, sig_ptr, sig_len);
    if (rc == 1) {
        printf("SUCCESS: SPDM measurement signature is VALID for %s\n", sysfs_dir);
        result = 0;
    } else {
        fprintf(stderr, "FAILURE: SPDM measurement signature verification FAILED!\n");
        result = -1;
    }

    EVP_MD_CTX_free(ctx);
    X509_free(cert);

cleanup:
    free(cert_buf);
    free(meas_buf);
    return result;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <sysfs_spdm_path>\n", argv[0]);
        return 1;
    }
    return verify_spdm_measurement(argv[1]) == 0 ? 0 : 1;
}
