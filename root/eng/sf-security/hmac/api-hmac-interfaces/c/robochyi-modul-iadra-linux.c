#include <linux/module.h>
#include <linux/crypto.h>
#include <crypto/hash.h>
#include <linux/err.h>
#include <linux/slab.h>

int kernel_compute_hmac_sha256(const u8 *key, unsigned int key_len,
                               const u8 *data, unsigned int data_len,
                               u8 *out_mac)
{
    struct crypto_shash *tfm;
    struct shash_desc *desc;
    int ret;

    /* 1. Виділення трансформації HMAC на базі SHA-256 */
    tfm = crypto_alloc_shash("hmac(sha256)", 0, 0);
    if (IS_ERR(tfm)) {
        pr_err("crypto_alloc_shash hmac(sha256) failed: %ld\n", PTR_ERR(tfm));
        return PTR_ERR(tfm);
    }

    /* 2. Встановлення секретного ключа */
    ret = crypto_shash_setkey(tfm, key, key_len);
    if (ret) {
        crypto_free_shash(tfm);
        return ret;
    }

    /* 3. Виділення пам'яті під дескриптор зі збереженням секретного стану */
    desc = kmalloc(sizeof(*desc) + crypto_shash_descsize(tfm), GFP_KERNEL);
    if (!desc) {
        crypto_free_shash(tfm);
        return -ENOMEM;
    }
    desc->tfm = tfm;

    /* 4. Одноразове обчислення дайджесту */
    ret = crypto_shash_digest(desc, data, data_len, out_mac);

    /* 5. Безпечне очищення чутливих даних дескриптора */
    kfree_sensitive(desc);
    crypto_free_shash(tfm);
    return ret;
}
