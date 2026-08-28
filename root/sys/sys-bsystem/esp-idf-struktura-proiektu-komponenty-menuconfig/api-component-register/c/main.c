/* Доступ до вбудованого ресурсу (C) */
#include <stdio.h>
#include <stdint.h>
#include "esp_log.h"

extern const uint8_t cert_pem_start[] asm("_binary_server_root_cert_pem_start");
extern const uint8_t cert_pem_end[]   asm("_binary_server_root_cert_pem_end");

void display_certificate_info(void) {
    const size_t size = (size_t)(cert_pem_end - cert_pem_start);
    printf("Розмір вбудованого сертифіката: %u байтів\n", (unsigned int)size);
}
