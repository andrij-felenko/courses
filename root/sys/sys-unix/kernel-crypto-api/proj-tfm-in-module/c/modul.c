// SPDX-License-Identifier: GPL-2.0
#include <linux/module.h>
#include <linux/slab.h>
#include <linux/scatterlist.h>
#include <linux/random.h>
#include <crypto/aead.h>

#define AAD_LEN  16      /* заголовок: автентифікуємо, але не ховаємо */
#define MSG_LEN  64
#define TAG_LEN  16      /* повний тег GCM */
#define IV_LEN   12      /* nonce GCM */

static const u8 msg[MSG_LEN] = "kernel crypto api demo: gcm(aes) over one kmalloc buffer";

/* Одна операція. Усе, що змінюється між викликами, задаємо наново. */
static int gcm_op(struct aead_request *req, struct scatterlist *sg,
                  struct crypto_wait *wait, const u8 *nonce, u8 *iv,
                  unsigned int cryptlen, bool encrypt)
{
        memcpy(iv, nonce, IV_LEN);            /* iv реалізація має право переписати */
        aead_request_set_ad(req, AAD_LEN);
        aead_request_set_crypt(req, sg, sg, cryptlen, iv);

        return crypto_wait_req(encrypt ? crypto_aead_encrypt(req)
                                       : crypto_aead_decrypt(req), wait);
}

static int __init gcmdemo_init(void)
{
        struct crypto_aead *tfm;
        struct aead_request *req = NULL;
        struct scatterlist sg;
        DECLARE_CRYPTO_WAIT(wait);             /* на стеку — і це правильно */
        u8 key[32], nonce[IV_LEN], iv[IV_LEN];
        u8 *buf = NULL;
        int err;

        tfm = crypto_alloc_aead("gcm(aes)", 0, 0);
        if (IS_ERR(tfm))
                return PTR_ERR(tfm);

        pr_info("gcmdemo: impl=%s ivsize=%u\n",
                crypto_tfm_alg_driver_name(crypto_aead_tfm(tfm)),
                crypto_aead_ivsize(tfm));

        if (crypto_aead_ivsize(tfm) != IV_LEN) {   /* розмір питають, а не знають */
                err = -EINVAL;
                goto out;
        }

        err = crypto_aead_setauthsize(tfm, TAG_LEN);
        if (err)
                goto out;

        get_random_bytes(key, sizeof(key));
        err = crypto_aead_setkey(tfm, key, sizeof(key));
        memzero_explicit(key, sizeof(key));    /* розгорнутий ключ уже всередині tfm */
        if (err)
                goto out;

        req = aead_request_alloc(tfm, GFP_KERNEL);
        if (!req) {
                err = -ENOMEM;
                goto out;
        }
        aead_request_set_callback(req,
                CRYPTO_TFM_REQ_MAY_BACKLOG | CRYPTO_TFM_REQ_MAY_SLEEP,
                crypto_req_done, &wait);

        buf = kmalloc(AAD_LEN + MSG_LEN + TAG_LEN, GFP_KERNEL);
        if (!buf) {
                err = -ENOMEM;
                goto out;
        }
        memset(buf, 0xa5, AAD_LEN);
        memcpy(buf + AAD_LEN, msg, MSG_LEN);
        memset(buf + AAD_LEN + MSG_LEN, 0, TAG_LEN);
        sg_init_one(&sg, buf, AAD_LEN + MSG_LEN + TAG_LEN);

        get_random_bytes(nonce, sizeof(nonce));

        err = gcm_op(req, &sg, &wait, nonce, iv, MSG_LEN, true);
        if (err)
                goto out;
        pr_info("gcmdemo: ct  %*ph\n", 16, buf + AAD_LEN);
        pr_info("gcmdemo: tag %*ph\n", TAG_LEN, buf + AAD_LEN + MSG_LEN);

        err = gcm_op(req, &sg, &wait, nonce, iv, MSG_LEN + TAG_LEN, false);
        if (err)
                goto out;
        pr_info("gcmdemo: back \"%s\"\n", (char *)(buf + AAD_LEN));

        /* Шифруємо ще раз — той самий nonce тут лише тому, що і текст, і ключ ті самі.
           У житті повторення nonce під тим самим ключем руйнує захист GCM. */
        err = gcm_op(req, &sg, &wait, nonce, iv, MSG_LEN, true);
        if (err)
                goto out;
        buf[0] ^= 0x01;                        /* один біт заголовка */
        err = gcm_op(req, &sg, &wait, nonce, iv, MSG_LEN + TAG_LEN, false);
        pr_info("gcmdemo: tampered AAD -> %d\n", err);
        err = (err == -EBADMSG) ? 0 : -EIO;
out:
        aead_request_free(req);   /* спершу запити: жоден не в польоті */
        crypto_free_aead(tfm);    /* тепер відпущено посилання на реалізацію */
        kfree_sensitive(buf);     /* там лежав відкритий текст */
        return err;
}

static void __exit gcmdemo_exit(void) { }

module_init(gcmdemo_init);
module_exit(gcmdemo_exit);
MODULE_DESCRIPTION("gcm(aes) end-to-end through the kernel crypto API");
MODULE_LICENSE("GPL");
