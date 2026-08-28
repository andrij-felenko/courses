size_t secret_len = 0;
// Крок 1: запит необхідного розміру буфера
if (EVP_PKEY_derive(ctx, nullptr, &secret_len) <= 0) {
    // Обробка помилки: неможливо визначити довжину секрету
}

std::vector<uint8_t> secret(secret_len);
// Крок 2: фактичне обчислення спільного секрету
if (EVP_PKEY_derive(ctx, secret.data(), &secret_len) <= 0) {
    // Обробка помилки: збій під час скалярного множення
}
