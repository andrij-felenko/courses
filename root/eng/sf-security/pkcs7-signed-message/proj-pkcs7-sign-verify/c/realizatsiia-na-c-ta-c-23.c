#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/bio.h>
#include <openssl/cms.h>
#include <openssl/err.h>
#include <openssl/pem.h>
#include <openssl/x509.h>
#include <openssl/x509_vfy.h>

/*
 * Створення відокремленого підпису CMS (Detached Signature)
 */
int cms_sign_detached(const char *data_file, const char *cert_file,
                      const char *key_file, const char *out_p7s_file) {
    int ret = 0;
    BIO *in_data = NULL;
    BIO *out_sig = NULL;
    BIO *cert_bio = NULL;
    BIO *key_bio = NULL;
    X509 *sign_cert = NULL;
    EVP_PKEY *sign_key = NULL;
    CMS_ContentInfo *cms = NULL;

    /* Завантаження сертифіката підписувача */
    cert_bio = BIO_new_file(cert_file, "r");
    if (!cert_bio) goto cleanup;
    sign_cert = PEM_read_bio_X509(cert_bio, NULL, NULL, NULL);
    if (!sign_cert) goto cleanup;

    /* Завантаження приватного ключа */
    key_bio = BIO_new_file(key_file, "r");
    if (!key_bio) goto cleanup;
    sign_key = PEM_read_bio_PrivateKey(key_bio, NULL, NULL, NULL);
    if (!sign_key) goto cleanup;

    /* Відкриття вхідного файлу даних */
    in_data = BIO_new_file(data_file, "rb");
    if (!in_data) goto cleanup;

    /*
     * CMS_sign з прапорцями:
     * - CMS_DETACHED: дані не вбудовуються в контейнер (eContent = NULL)
     * - CMS_BINARY: заборона MIME-канонізації CRLF (бінарна прошивка)
     * - CMS_NOSMIMECAP: не додавати застарілі S/MIME можливості
     * - CMS_STREAM: увімкнення потокового однопрохідного режиму
     */
    unsigned int flags = CMS_DETACHED | CMS_BINARY | CMS_NOSMIMECAP | CMS_STREAM;
    cms = CMS_sign(sign_cert, sign_key, NULL, in_data, flags);
    if (!cms) goto cleanup;

    /* Створення вихідного файлу для підпису DER/PEM */
    out_sig = BIO_new_file(out_p7s_file, "wb");
    if (!out_sig) goto cleanup;

    /* Потоковий запис CMS структури в DER форматі */
    if (!i2d_CMS_bio_stream(out_sig, cms, in_data, flags)) {
        goto cleanup;
    }

    ret = 1; /* Успіх */

cleanup:
    if (!ret) {
        ERR_print_errors_fp(stderr);
    }
    CMS_ContentInfo_free(cms);
    BIO_free(in_data);
    BIO_free(out_sig);
    BIO_free(cert_bio);
    BIO_free(key_bio);
    X509_free(sign_cert);
    EVP_PKEY_free(sign_key);
    return ret;
}

/*
 * Потокова верифікація відокремленого підпису CMS
 */
int cms_verify_detached(const char *data_file, const char *sig_p7s_file,
                        const char *ca_file) {
    int ret = 0;
    BIO *in_data = NULL;
    BIO *in_sig = NULL;
    CMS_ContentInfo *cms = NULL;
    X509_STORE *store = NULL;

    /* Створення довіреного сховища сертифікатів CA */
    store = X509_STORE_new();
    if (!store) goto cleanup;
    if (!X509_STORE_load_locations(store, ca_file, NULL)) {
        goto cleanup;
    }

    /* Зчитування CMS структури підпису */
    in_sig = BIO_new_file(sig_p7s_file, "rb");
    if (!in_sig) goto cleanup;
    cms = d2i_CMS_bio(in_sig, NULL);
    if (!cms) goto cleanup;

    /* Відкриття бінарного файлу даних */
    in_data = BIO_new_file(data_file, "rb");
    if (!in_data) goto cleanup;

    /*
     * Потокова верифікація CMS_verify:
     * - in_data: зовнішній відкритий потік даних
     * - store: довірений якір Root CA
     * - CMS_BINARY: суворе побайтове читання без перетворень
     */
    unsigned int flags = CMS_BINARY;
    if (CMS_verify(cms, NULL, store, in_data, NULL, flags) <= 0) {
        goto cleanup;
    }

    ret = 1; /* Підпис валідний і ланцюг довірений */

cleanup:
    if (!ret) {
        ERR_print_errors_fp(stderr);
    }
    CMS_ContentInfo_free(cms);
    BIO_free(in_data);
    BIO_free(in_sig);
    X509_STORE_free(store);
    return ret;
}
