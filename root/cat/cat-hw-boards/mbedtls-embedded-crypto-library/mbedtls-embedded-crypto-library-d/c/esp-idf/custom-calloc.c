#include "mbedtls/ssl.h"
#include "mbedtls/platform.h"
#include <stdlib.h>

// Приклад власних функцій розподілу пам'яті для упередження фрагментації купи
static void *custom_calloc(size_t n, size_t size) {
    return calloc(n, size);
}

static void custom_free(void *ptr) {
    free(ptr);
}

// Конфігурування MFLN та пам'яткового бюджету TLS
int configure_mbedtls_memory(mbedtls_ssl_config *conf) {
    // 1. Реєстрація кастомного виділювача пам'яті
    mbedtls_platform_set_calloc_free(custom_calloc, custom_free);
    
    // 2. Встановлення обмеження MFLN до 1024 байтів (MBEDTLS_SSL_MAX_FRAG_LEN_1024)
    int ret = mbedtls_ssl_conf_max_frag_len(conf, MBEDTLS_SSL_MAX_FRAG_LEN_1024);
    if (ret != 0) {
        return ret;
    }
    
    return 0;
}
