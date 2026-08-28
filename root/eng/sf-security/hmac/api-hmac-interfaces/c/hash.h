#include <crypto/hash.h>
#include <linux/crypto.h>

/* Виділення та звільнення трансформації алгоритму */
struct crypto_shash *crypto_alloc_shash(const char *alg_name, u32 type, u32 mask);
void crypto_free_shash(struct crypto_shash *tfm);

/* Встановлення таємного ключа сесії */
int crypto_shash_setkey(struct crypto_shash *tfm, const u8 *key, unsigned int keylen);

/* Одноразове обчислення підпису над неперервним буфером */
int crypto_shash_digest(struct shash_desc *desc, const u8 *data, unsigned int len, u8 *out);

/* Потоковий API для фрагментованих пакетів (sk_buff) */
int crypto_shash_init(struct shash_desc *desc);
int crypto_shash_update(struct shash_desc *desc, const u8 *data, unsigned int len);
int crypto_shash_final(struct shash_desc *desc, u8 *out);
