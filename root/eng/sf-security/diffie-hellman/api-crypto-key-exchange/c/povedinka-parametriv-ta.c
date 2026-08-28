size_t secret_len = 0;
/* Крок 1: запит необхідного розміру буфера */
if (EVP_PKEY_derive(ctx, NULL, &secret_len) <= 0) {
    /* Обробка помилки: неможливо визначити довжину секрету */
}

uint8_t *secret = (uint8_t*)malloc(secret_len);
/* Крок 2: фактичне обчислення спільного секрету */
if (!secret || EVP_PKEY_derive(ctx, secret, &secret_len) <= 0) {
    /* Обробка помилки: збій під час скалярного множення */
}
