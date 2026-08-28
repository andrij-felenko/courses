#include <linux/module.h>
#include <linux/crypto.h>
#include <crypto/hash.h>
#include <linux/err.h>
#include <linux/slab.h>

int kernel_compute_cmac_aes(const u8 *key, unsigned int key_len,
                            const u8 *data, unsigned int data_len,
                            u8 *out_tag) {
    struct crypto_shash *tfm;
    struct shash_desc *desc;
    int desc_size;
    int ret;

    /* 1. Виділення дескриптора трансформації алгоритму CMAC на базі AES */
    tfm = crypto_alloc_shash("cmac(aes)", 0, 0);
    if (IS_ERR(tfm)) {
        pr_err("crypto_alloc_shash failed: %ld\n", PTR_ERR(tfm));
        return PTR_ERR(tfm);
    }

    /* 2. Прив'язка ключа (драйвер генерує внутрішні підключі K1 та K2) */
    ret = crypto_shash_setkey(tfm, key, key_len);
    if (ret) {
        pr_err("crypto_shash_setkey failed: %d\n", ret);
        goto free_tfm;
    }

    /* 3. Виділення пам'яті під дескриптор запиту з урахуванням descsize */
    desc_size = sizeof(struct shash_desc) + crypto_shash_descsize(tfm);
    desc = kmalloc(desc_size, GFP_KERNEL);
    if (!desc) {
        ret = -ENOMEM;
        goto free_tfm;
    }
    desc->tfm = tfm;

    /* 4. Однопрохідне обчислення тегу (ініціалізація, оновлення, фіналізація) */
    ret = crypto_shash_digest(desc, data, data_len, out_tag);
    if (ret) {
        pr_err("crypto_shash_digest failed: %d\n", ret);
    }

    /* 5. Безпечне очищення чутливих структур даних перед звільненням */
    kfree_sensitive(desc);

free_tfm:
    crypto_free_shash(tfm);
    return ret;
}

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("CMAC-AES Kernel Crypto API example");
