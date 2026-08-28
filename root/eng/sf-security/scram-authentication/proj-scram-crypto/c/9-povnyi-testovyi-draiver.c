/* Тестовий драйвер перевірки еталонних векторів RFC 7677 */
int run_rfc7677_test_suite(void) {
    const char *password = "pencil";
    const uint8_t salt[12] = {
        0x41, 0x25, 0xc2, 0x47, 0xe4, 0x3a, 0xb1, 0xe9, 0x3c, 0x6d, 0xff, 0x76
    };
    int iterations = 4096;
    const char *auth_message =
        "n=user,r=fyko+d2lbbFgONRv9qkxdawL,"
        "r=fyko+d2lbbFgONRv9qkxdawL3rfcNHYJY1ZVvWVs7j,s=QSXCR+Q6sek8bf92,"
        "i=4096,c=biws,r=fyko+d2lbbFgONRv9qkxdawL3rfcNHYJY1ZVvWVs7j";

    uint8_t salted_password[SCRAM_SHA256_HASH_SIZE];
    uint8_t client_key[SCRAM_SHA256_HASH_SIZE];
    uint8_t stored_key[SCRAM_SHA256_HASH_SIZE];
    uint8_t server_key[SCRAM_SHA256_HASH_SIZE];
    uint8_t client_proof[SCRAM_SHA256_HASH_SIZE];
    uint8_t server_signature[SCRAM_SHA256_HASH_SIZE];

    /* Очікуваний результат ClientProof згідно з RFC 7677 (Base64 v0X8...) */
    const uint8_t expected_client_proof[SCRAM_SHA256_HASH_SIZE] = {
        0x8d, 0xa6, 0x49, 0xbf, 0x70, 0x73, 0xd9, 0x3d,
        0x02, 0x24, 0x66, 0xc9, 0x43, 0x01, 0x74, 0x5f,
        0xe1, 0xc8, 0xa2, 0x2a, 0x6f, 0x7f, 0x40, 0x65,
        0x66, 0x83, 0xaa, 0x83, 0x6a, 0x34, 0xe5, 0x55
    };

    /* 1. Обчислення SaltedPassword */
    if (scram_compute_salted_password(password, strlen(password),
                                      salt, sizeof(salt), iterations,
                                      salted_password) != 0) {
        return -1;
    }

    /* 2. Виведення ключів */
    if (scram_derive_key_triad(salted_password, client_key, stored_key, server_key) != 0) {
        return -2;
    }

    /* 3. Формування ClientProof */
    if (scram_create_client_proof(client_key, stored_key,
                                  auth_message, strlen(auth_message),
                                  client_proof) != 0) {
        return -3;
    }

    /* Звірка отриманого ClientProof з еталоном */
    if (memcmp(client_proof, expected_client_proof, SCRAM_SHA256_HASH_SIZE) != 0) {
        return -4; /* Помилка: доказ не збігся з вектором RFC 7677 */
    }

    /* 4. Серверна верифікація та генерація ServerSignature */
    if (scram_verify_proof_and_generate_server_signature(
            stored_key, server_key, client_proof,
            auth_message, strlen(auth_message), server_signature) != 0) {
        return -5;
    }

    /* 5. Клієнтська верифікація ServerSignature */
    if (scram_client_verify_server_signature(server_key, auth_message,
                                             strlen(auth_message), server_signature) != 0) {
        return -6;
    }

    return 0; /* Усі тести пройдено успішно */
}
