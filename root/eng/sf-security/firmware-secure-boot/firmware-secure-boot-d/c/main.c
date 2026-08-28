// Одна ланка ланцюга довіри: перевірити наступний образ — і лише тоді стрибнути.
// root_key_digest — відбиток відкритого ключа, «перепалений» у запобіжниках (незмінний).

typedef void (*entry_fn)(void);   // точка входу наступної ланки

bool verify_image(const image_t *img, const uint8_t root_key_digest[32]) {
    // 1. відкритий ключ лежить у блоці підпису образу — та довіряти йому ще зарано:
    //    звіряємо його відбиток із тим, що «перепалений» у запобіжниках.
    uint8_t key_digest[32];
    sha256(img->pubkey, img->pubkey_len, key_digest);
    if (memcmp(key_digest, root_key_digest, 32) != 0)
        return false;             // ключ не той, що в запобіжниках → образ чужий

    // 2. ключу можна вірити — тепер ним звіряємо підпис над тілом образу
    uint8_t body_digest[32];
    sha256(img->body, img->body_len, body_digest);
    return rsa_pss_verify(img->pubkey, img->signature, body_digest);  // збіг → справжній
}

void boot_next(const image_t *img, const uint8_t root_key_digest[32]) {
    if (!verify_image(img, root_key_digest)) {
        halt();                   // підпис не той → НЕ стартуємо, ланцюг обірвано
    }
    entry_fn next = (entry_fn) img->entry;
    next();                       // перевірено → лише тепер віддаємо керування
}
