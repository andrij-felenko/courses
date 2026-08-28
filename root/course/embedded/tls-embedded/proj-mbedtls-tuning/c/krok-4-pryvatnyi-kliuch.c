#include "psa/crypto.h"
#include "mbedtls/pk.h"

static mbedtls_pk_context  own_key;   // ОБГОРТКА на ключ, а не сам ключ
static mbedtls_x509_crt    own_cert;  // наш власний сертифікат (публічна частина)

int tls_setup_own_identity(psa_key_id_t key_in_secure_element) {
    // передумова: MBEDTLS_USE_PSA_CRYPTO увімкнено у config.h, і на старті
    // викликано psa_crypto_init(). Ключ уже живе в захищеному елементі —
    // народжений там, назовні не виходив НІКОЛИ.
    if (psa_crypto_init() != PSA_SUCCESS)
        return -1;

    mbedtls_pk_init(&own_key);

    // ★ обгорнути РУЧКУ на ключ у PK-контекст. Сам приватний ключ сюди
    //    НЕ копіюється — own_key лише знає, кого просити про підпис.
    if (mbedtls_pk_setup_opaque(&own_key, key_in_secure_element) != 0)
        return -1;

    // наш публічний сертифікат розбираємо як звичайно (він не секрет).
    mbedtls_x509_crt_init(&own_cert);
    // ... mbedtls_x509_crt_parse(&own_cert, own_cert_pem, own_cert_pem_len) ...

    // ★ віддати конфігу нашу пару: сертифікат (публічний) + opaque-ключ.
    //    коли сервер попросить довести особу, mbedTLS НЕ візьме ключ — вона
    //    попросить захищений елемент підписати транскрипт і отримає лише підпис.
    if (mbedtls_ssl_conf_own_cert(&conf, &own_cert, &own_key) != 0)
        return -1;

    return 0;
}
