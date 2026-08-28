// mbedtls_config.h — лишаємо РІВНО потрібне, решту крипто викидаємо з Flash.

// протокол: тільки TLS 1.3 (старіші версії — геть, це десятки КБ коду).
#define MBEDTLS_SSL_PROTO_TLS1_3
// (не визначаємо MBEDTLS_SSL_PROTO_TLS1_2 — 1.2 нам не треба)

// AEAD: лишаємо AES-GCM (є апаратний AES). ChaCha20 нам не потрібен —
// не визначаємо MBEDTLS_CHACHAPOLY_C і MBEDTLS_CHACHA20_C.
#define MBEDTLS_GCM_C
#define MBEDTLS_AES_C
#define MBEDTLS_SHA256_C          // геш для key schedule і для AES-GCM-SHA256

// крива: тільки X25519. Решту еліптичних груп не вмикаємо.
#define MBEDTLS_ECDH_C
#define MBEDTLS_ECP_DP_CURVE25519_ENABLED
// (жодних MBEDTLS_ECP_DP_SECP*_ENABLED, якщо сервер їх не вимагає)

// підпис у сертифікаті сервера — під його реальний алгоритм (напр. ECDSA):
#define MBEDTLS_ECDSA_C
#define MBEDTLS_X509_CRT_PARSE_C  // розбір сертифіката сервера

// сухий залишок: одна крива, один AEAD, один геш, розбір X.509 — і все.
// зайвих реалізацій у Flash немає, а отже й місць, де ховається вада, менше.
