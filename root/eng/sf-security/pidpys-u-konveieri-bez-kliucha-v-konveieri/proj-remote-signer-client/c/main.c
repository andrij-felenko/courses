#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <openssl/evp.h>
#include <openssl/bio.h>
#include <openssl/ssl.h>
#include <openssl/err.h>

#define CHUNK_SIZE 8192
#define DIGEST_LEN 32

/* Обчислення SHA-256 дайджесту файлу через OpenSSL EVP API */
int compute_sha256(const char *filepath, uint8_t *digest_out) {
    FILE *fp = fopen(filepath, "rb");
    if (!fp) {
        perror("Помилка відкриття файлу для гешування");
        return -1;
    }

    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    if (!mdctx) {
        fclose(fp);
        return -1;
    }

    if (EVP_DigestInit_ex(mdctx, EVP_sha256(), NULL) != 1) {
        EVP_MD_CTX_free(mdctx);
        fclose(fp);
        return -1;
    }

    uint8_t buffer[CHUNK_SIZE];
    size_t bytes_read = 0;
    while ((bytes_read = fread(buffer, 1, sizeof(buffer), fp)) > 0) {
        if (EVP_DigestUpdate(mdctx, buffer, bytes_read) != 1) {
            EVP_MD_CTX_free(mdctx);
            fclose(fp);
            return -1;
        }
    }

    unsigned int len = 0;
    if (EVP_DigestFinal_ex(mdctx, digest_out, &len) != 1 || len != DIGEST_LEN) {
        EVP_MD_CTX_free(mdctx);
        fclose(fp);
        return -1;
    }

    EVP_MD_CTX_free(mdctx);
    fclose(fp);
    return 0;
}

/* Перетворення бінарного дайджесту в шістнадцятковий рядок */
void digest_to_hex(const uint8_t *digest, char *hex_out) {
    for (int i = 0; i < DIGEST_LEN; ++i) {
        sprintf(hex_out + (i * 2), "%02x", digest[i]);
    }
    hex_out[DIGEST_LEN * 2] = '\0';
}

/* Виконання mTLS запиту до служби підпису */
int send_remote_sign_request(
    const char *host_port,
    const char *ca_cert_path,
    const char *client_cert_path,
    const char *client_key_path,
    const char *json_payload,
    char *response_out,
    size_t response_max_len
) {
    SSL_CTX *ctx = SSL_CTX_new(TLS_client_method());
    if (!ctx) return -1;

    SSL_CTX_set_min_proto_version(ctx, TLS1_3_VERSION);

    /* Завантаження довіреного CA сертифіката */
    if (SSL_CTX_load_verify_locations(ctx, ca_cert_path, NULL) != 1) {
        SSL_CTX_free(ctx);
        return -1;
    }

    /* Завантаження клієнтського сертифіката mTLS для раннера */
    if (client_cert_path && client_key_path) {
        if (SSL_CTX_use_certificate_file(ctx, client_cert_path, SSL_FILETYPE_PEM) != 1 ||
            SSL_CTX_use_PrivateKey_file(ctx, client_key_path, SSL_FILETYPE_PEM) != 1) {
            SSL_CTX_free(ctx);
            return -1;
        }
    }

    BIO *bio = BIO_new_ssl_connect(ctx);
    if (!bio) {
        SSL_CTX_free(ctx);
        return -1;
    }

    BIO_set_conn_hostname(bio, host_port);

    SSL *ssl = NULL;
    BIO_get_ssl(bio, &ssl);
    if (!ssl) {
        BIO_free_all(bio);
        SSL_CTX_free(ctx);
        return -1;
    }

    SSL_set_tlsext_host_name(ssl, "signing.internal.acme.net");

    if (BIO_do_connect(bio) <= 0) {
        BIO_free_all(bio);
        SSL_CTX_free(ctx);
        return -1;
    }

    /* Формування HTTP/1.1 POST повідомлення */
    char http_header[1024];
    int header_len = snprintf(
        http_header, sizeof(http_header),
        "POST /api/v1/sign HTTP/1.1\r\n"
        "Host: %s\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: %zu\r\n"
        "Connection: close\r\n\r\n",
        "signing.internal.acme.net",
        strlen(json_payload)
    );

    BIO_write(bio, http_header, header_len);
    BIO_write(bio, json_payload, strlen(json_payload));

    int total_read = 0;
    int bytes = 0;
    while ((bytes = BIO_read(bio, response_out + total_read, response_max_len - total_read - 1)) > 0) {
        total_read += bytes;
    }
    response_out[total_read] = '\0';

    BIO_free_all(bio);
    SSL_CTX_free(ctx);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <артефакт> <oidc_token>\n", argv[0]);
        return 1;
    }

    const char *artifact_path = argv[1];
    const char *oidc_token = argv[2];
    uint8_t digest[DIGEST_LEN];

    if (compute_sha256(artifact_path, digest) != 0) {
        fprintf(stderr, "Помилка обчислення гешу від %s\n", artifact_path);
        return 1;
    }

    char hex_digest[DIGEST_LEN * 2 + 1];
    digest_to_hex(digest, hex_digest);

    char json_request[2048];
    snprintf(
        json_request, sizeof(json_request),
        "{\"digest\":\"%s\",\"algorithm\":\"ECDSA_P256\",\"oidc_token\":\"%s\",\"key_alias\":\"firmware-prod\"}",
        hex_digest, oidc_token
    );

    char response[8192];
    if (send_remote_sign_request("10.240.12.45:8443", "ca.crt", "runner.crt", "runner.key", json_request, response, sizeof(response)) != 0) {
        fprintf(stderr, "Помилка зв'язку зі службою підпису\n");
        return 1;
    }

    printf("Отримано відповідь від служби підпису:\n%s\n", response);
    return 0;
}
