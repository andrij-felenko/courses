#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#include "mbedtls/net_sockets.h"
#include "mbedtls/ssl.h"
#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"
#include "mbedtls/x509_crt.h"
#include "mbedtls/pk.h"
#include "mbedtls/asn1write.h"
#include "mbedtls/error.h"

#define SE_SLOT_IDEVID_KEY 0x00
#define SE_SLOT_LDEVID_KEY 0x01

/* Структура представлення апаратного модуля безпеки */
typedef struct {
    uint8_t chip_uid[16];
    size_t  uid_len;
    uint8_t active_slot;
} hardware_security_module_t;

/* Зчитування унікального апаратного ідентифікатора кремнію */
int hsm_read_silicon_uid(hardware_security_module_t *hsm) {
    if (!hsm) return -1;
    /* У реальній системі: зчитування eFuse або регістрів UID мікроконтролера */
    const uint8_t mock_uid[16] = {
        0x53, 0x54, 0x4D, 0x33, 0x32, 0x48, 0x35, 0x30,
        0xAA, 0xBB, 0xCC, 0xDD, 0x01, 0x02, 0x03, 0x04
    };
    memcpy(hsm->chip_uid, mock_uid, sizeof(mock_uid));
    hsm->uid_len = sizeof(mock_uid);
    hsm->active_slot = SE_SLOT_IDEVID_KEY;
    return 0;
}

/* Апаратний підпис гешу: приватний ключ ніколи не виходить за межі чипа */
int hsm_ecdsa_sign_hash(hardware_security_module_t *hsm,
                        const uint8_t *hash, size_t hash_len,
                        uint8_t *sig_r, uint8_t *sig_s,
                        size_t *sig_comp_len) {
    if (!hsm || !hash || hash_len != 32 || !sig_r || !sig_s) return -1;
    
    /* Відправлення команди підпису на Secure Element через шину I2C */
    /* Чип обчислює ECDSA над наданим дайджестом і повертає числа r та s */
    memset(sig_r, 0xA5, 32);
    memset(sig_s, 0x5A, 32);
    *sig_comp_len = 32;
    return 0;
}

/* Зворотний виклик mbedTLS для непрозорого (opaque) ключа */
static int opaque_ecdsa_sign_callback(mbedtls_pk_context *ctx,
                                      mbedtls_md_type_t md_alg,
                                      const unsigned char *hash, size_t hash_len,
                                      unsigned char *sig, size_t *sig_len,
                                      int (*f_rng)(void *, unsigned char *, size_t),
                                      void *p_rng) {
    (void)md_alg; (void)f_rng; (void)p_rng;
    hardware_security_module_t *hsm = (hardware_security_module_t *)ctx->pk_ctx;
    
    uint8_t r[32], s[32];
    size_t comp_len = 0;
    
    if (hsm_ecdsa_sign_hash(hsm, hash, hash_len, r, s, &comp_len) != 0) {
        return MBEDTLS_ERR_PK_BAD_INPUT_DATA;
    }
    
    /* Формування ASN.1 DER структури ECDSA-Sig-Value: SEQUENCE { r INTEGER, s INTEGER } */
    unsigned char *p = sig + 72;
    int len = 0;
    
    mbedtls_mpi r_mpi, s_mpi;
    mbedtls_mpi_init(&r_mpi);
    mbedtls_mpi_init(&s_mpi);
    
    mbedtls_mpi_read_binary(&r_mpi, r, comp_len);
    mbedtls_mpi_read_binary(&s_mpi, s, comp_len);
    
    mbedtls_asn1_write_mpi(&p, sig, &s_mpi);
    mbedtls_asn1_write_mpi(&p, sig, &r_mpi);
    len = (int)(sig + 72 - p);
    mbedtls_asn1_write_len(&p, sig, len);
    mbedtls_asn1_write_tag(&p, sig, MBEDTLS_ASN1_CONSTRUCTED | MBEDTLS_ASN1_SEQUENCE);
    
    *sig_len = (size_t)(sig + 72 - p);
    memmove(sig, p, *sig_len);
    
    mbedtls_mpi_free(&r_mpi);
    mbedtls_mpi_free(&s_mpi);
    return 0;
}

/* Запуск mTLS клієнта з використанням апаратного ключа */
int run_device_mtls_client(const char *server_host, const char *server_port,
                           const char *ca_cert_pem, const char *dev_cert_pem) {
    int ret = 0;
    hardware_security_module_t hsm;
    if (hsm_read_silicon_uid(&hsm) != 0) {
        fprintf(stderr, "Помилка читання UID чипа\n");
        return -1;
    }

    mbedtls_net_context      server_fd;
    mbedtls_ssl_context      ssl;
    mbedtls_ssl_config       conf;
    mbedtls_x509_crt         cacert;
    mbedtls_x509_crt         clicert;
    mbedtls_pk_context       pkey;
    mbedtls_entropy_context  entropy;
    mbedtls_ctr_drbg_context ctr_drbg;

    mbedtls_net_init(&server_fd);
    mbedtls_ssl_init(&ssl);
    mbedtls_ssl_config_init(&conf);
    mbedtls_x509_crt_init(&cacert);
    mbedtls_x509_crt_init(&clicert);
    mbedtls_pk_init(&pkey);
    mbedtls_ctr_drbg_init(&ctr_drbg);
    mbedtls_entropy_init(&entropy);

    const char *pers = "device_identity_mtls";
    if (mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
                              (const unsigned char *)pers, strlen(pers)) != 0) {
        ret = -1;
        goto cleanup;
    }

    /* Завантаження CA та сертифіката пристрою */
    if (mbedtls_x509_crt_parse(&cacert, (const unsigned char *)ca_cert_pem, strlen(ca_cert_pem) + 1) != 0 ||
        mbedtls_x509_crt_parse(&clicert, (const unsigned char *)dev_cert_pem, strlen(dev_cert_pem) + 1) != 0) {
        ret = -2;
        goto cleanup;
    }

    /* Налаштування непрозорого контексту відкритого ключа */
    pkey.pk_info = mbedtls_pk_info_from_type(MBEDTLS_PK_OPAQUE);
    pkey.pk_ctx  = &hsm;

    if (mbedtls_ssl_config_defaults(&conf, MBEDTLS_SSL_IS_CLIENT,
                                    MBEDTLS_SSL_TRANSPORT_STREAM,
                                    MBEDTLS_SSL_PRESET_DEFAULT) != 0) {
        ret = -3;
        goto cleanup;
    }

    mbedtls_ssl_conf_authmode(&conf, MBEDTLS_SSL_VERIFY_REQUIRED);
    mbedtls_ssl_conf_ca_chain(&conf, &cacert, NULL);
    mbedtls_ssl_conf_own_cert(&conf, &clicert, &pkey);
    mbedtls_ssl_conf_rng(&conf, mbedtls_ctr_drbg_random, &ctr_drbg);

    if (mbedtls_ssl_setup(&ssl, &conf) != 0) {
        ret = -4;
        goto cleanup;
    }

    if (mbedtls_ssl_set_hostname(&ssl, server_host) != 0) {
        ret = -5;
        goto cleanup;
    }

    /* Встановлення мережевого TCP з'єднання */
    if (mbedtls_net_connect(&server_fd, server_host, server_port, MBEDTLS_NET_PROTO_TCP) != 0) {
        ret = -6;
        goto cleanup;
    }
    mbedtls_ssl_set_bio(&ssl, &server_fd, mbedtls_net_send, mbedtls_net_recv, NULL);

    /* Виконання TLS рукостискання */
    while ((ret = mbedtls_ssl_handshake(&ssl)) != 0) {
        if (ret != MBEDTLS_ERR_SSL_WANT_READ && ret != MBEDTLS_ERR_SSL_WANT_WRITE) {
            fprintf(stderr, "Помилка TLS рукостискання: -0x%04X\n", -ret);
            goto cleanup;
        }
    }

    printf("mTLS сесію успішно встановлено з сервером %s:%s\n", server_host, server_port);
    ret = 0;

cleanup:
    mbedtls_net_free(&server_fd);
    mbedtls_x509_crt_free(&clicert);
    mbedtls_x509_crt_free(&cacert);
    mbedtls_pk_free(&pkey);
    mbedtls_ssl_free(&ssl);
    mbedtls_ssl_config_free(&conf);
    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);
    return ret;
}
