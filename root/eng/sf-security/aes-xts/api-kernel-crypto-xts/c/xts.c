/* Фрагмент реалізації crypto/xts.c у ядрі Linux */
static int xts_setkey(struct crypto_skcipher *tfm, const u8 *key, unsigned int keylen) {
    /* Перевірка мінімальної та максимальної довжини ключа */
    if (keylen != 32 && keylen != 64)
        return -EINVAL;

    /* Вимога FIPS 140-3: заборона збігу Key1 та Key2 */
    if (crypto_fips_enabled || IS_ENABLED(CONFIG_CRYPTO_FIPS)) {
        if (!crypto_memneq(key, key + (keylen / 2), keylen / 2))
            return -EINVAL;
    }
    /* Ініціалізація підлеглих контекстів Key1 та Key2 */
    ...
}
