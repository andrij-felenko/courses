struct crypto_aead *tfm;
struct aead_request *req;
DECLARE_CRYPTO_WAIT(wait);
struct scatterlist sg[3];
int err;

tfm = crypto_alloc_aead("gcm(aes)", 0, 0);
if (IS_ERR(tfm))
        return PTR_ERR(tfm);

err = crypto_aead_setkey(tfm, key, 32);            /* AES-256 */
if (!err)
        err = crypto_aead_setauthsize(tfm, 16);    /* тег 16 байтів */
if (err)
        goto out_free_tfm;

req = aead_request_alloc(tfm, GFP_KERNEL);
if (!req) {
        err = -ENOMEM;
        goto out_free_tfm;
}

sg_init_table(sg, 3);
sg_set_buf(&sg[0], ad,   ad_len);     /* лише автентифікується */
sg_set_buf(&sg[1], data, data_len);   /* шифрується на місці */
sg_set_buf(&sg[2], tag,  16);         /* сюди ляже тег */

aead_request_set_callback(req,
        CRYPTO_TFM_REQ_MAY_BACKLOG | CRYPTO_TFM_REQ_MAY_SLEEP,
        crypto_req_done, &wait);
aead_request_set_ad(req, ad_len);
aead_request_set_crypt(req, sg, sg, data_len, iv);

err = crypto_wait_req(crypto_aead_encrypt(req), &wait);
