#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/crypto.h>
#include <crypto/internal/hash.h>
#include <linux/unaligned.h>  /* до ядра 6.12 заголовок звався <asm/unaligned.h> */

struct my_digest_ctx {
    u32 state;
    u64 count;
};

static int my_hash_init(struct shash_desc *desc)
{
    struct my_digest_ctx *ctx = shash_desc_ctx(desc);
    ctx->state = 0x811c9dc5; /* FNV offset basis */
    ctx->count = 0;
    return 0;
}

static int my_hash_update(struct shash_desc *desc, const u8 *data, unsigned int len)
{
    struct my_digest_ctx *ctx = shash_desc_ctx(desc);
    unsigned int i;
    for (i = 0; i < len; i++) {
        ctx->state ^= data[i];
        ctx->state *= 0x01000193; /* FNV prime */
        ctx->count++;
    }
    return 0;
}

static int my_hash_final(struct shash_desc *desc, u8 *out)
{
    struct my_digest_ctx *ctx = shash_desc_ctx(desc);
    put_unaligned_le32(ctx->state, out);
    return 0;
}

static struct shash_alg my_shash_alg = {
    .digestsize = 4,
    .descsize   = sizeof(struct my_digest_ctx),
    .init       = my_hash_init,
    .update     = my_hash_update,
    .final      = my_hash_final,
    .base       = {
        .cra_name        = "myfnv1a",
        .cra_driver_name = "myfnv1a-generic",
        .cra_priority    = 100,
        .cra_blocksize   = 1,
        .cra_module      = THIS_MODULE,
    }
};

static int __init my_crypto_provider_init(void)
{
    int err = crypto_register_shash(&my_shash_alg);
    if (err)
        pr_err("Помилка реєстрації myfnv1a: %d\n", err);
    else
        pr_info("Криптопровайдер myfnv1a успішно зареєстровано\n");
    return err;
}

static void __exit my_crypto_provider_exit(void)
{
    crypto_unregister_shash(&my_shash_alg);
    pr_info("Криптопровайдер myfnv1a вивантажено\n");
}

module_init(my_crypto_provider_init);
module_exit(my_crypto_provider_exit);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Приклад власного криптографічного провайдера для Kernel Crypto API");
