/* Фрагмент виділення трансформації та завантаження ключа в ядрі Linux */
struct crypto_skcipher *tfm = crypto_alloc_skcipher("xts(aes)", 0, 0);
if (IS_ERR(tfm)) {
    return PTR_ERR(tfm);
}

/* Встановлення 512-бітного ключа XTS */
int ret = crypto_skcipher_setkey(tfm, raw_key_512, 64);
if (ret < 0) {
    crypto_free_skcipher(tfm);
    return ret;
}
