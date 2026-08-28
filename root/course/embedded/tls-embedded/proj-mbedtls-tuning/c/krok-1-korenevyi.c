#include "mbedtls/ssl.h"
#include "mbedtls/x509_crt.h"
#include "mbedtls/ctr_drbg.h"
#include "mbedtls/entropy.h"

// кореневий сертифікат CA нашого сервера — зашитий у прошивку (PEM у Flash).
// саме ним ми перевірятимемо, що сервер справді наш.
extern const char ca_pem[];          // "----BEGIN CERTIFICATE----\n...\n----END..."
extern const size_t ca_pem_len;      // ДОВЖИНА разом із завершальним нулем!

static mbedtls_x509_crt      cacert;   // сюди розберемо кореневий сертифікат
static mbedtls_ssl_config    conf;     // конфіг з'єднання
static mbedtls_ssl_context   ssl;      // сама сесія
static mbedtls_entropy_context   entropy;
static mbedtls_ctr_drbg_context  ctr_drbg;

int tls_client_init(void) {
    mbedtls_x509_crt_init(&cacert);
    mbedtls_ssl_config_init(&conf);
    mbedtls_ssl_init(&ssl);
    mbedtls_ctr_drbg_init(&ctr_drbg);
    mbedtls_entropy_init(&entropy);

    // джерело випадковості для рукостискання (одноразові частки, nonce).
    // без справжньої ентропії весь ECDHE стає передбачуваним — це теж діра.
    if (mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
                              NULL, 0) != 0)
        return -1;

    // РОЗБІР кореневого сертифіката. Тонкість PEM: довжина МУСИТЬ включати
    // завершальний нульовий байт, інакше mbedtls_x509_crt_parse не впізнає PEM
    // і мовчки спробує тлумачити його як (невдалий) DER → порожній ланцюг.
    int ret = mbedtls_x509_crt_parse(&cacert,
                                     (const unsigned char *)ca_pem, ca_pem_len);
    if (ret != 0) {
        // ret < 0 тут — НАЙПІДСТУПНІША помилка: ланцюг довіри порожній,
        // і якщо її не зловити, перевіряти сервер буде НІЧИМ.
        return -1;   // зупиняємось: без кореня далі йти НЕ можна
    }
    return 0;
}
