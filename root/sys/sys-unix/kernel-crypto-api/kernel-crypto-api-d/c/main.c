DECLARE_CRYPTO_WAIT(wait);
struct crypto_skcipher *tfm;
struct skcipher_request *req;
int err;

tfm = crypto_alloc_skcipher("xts(aes)", 0, 0);
if (IS_ERR(tfm))
        return PTR_ERR(tfm);

err = crypto_skcipher_setkey(tfm, key, 64);   /* два ключі по 32 байти */
if (err)
        goto out_free_tfm;

req = skcipher_request_alloc(tfm, GFP_KERNEL);
if (!req) {
        err = -ENOMEM;
        goto out_free_tfm;
}

skcipher_request_set_callback(req,
        CRYPTO_TFM_REQ_MAY_BACKLOG | CRYPTO_TFM_REQ_MAY_SLEEP,
        crypto_req_done, &wait);
skcipher_request_set_crypt(req, sg_in, sg_out, len, iv);

err = crypto_wait_req(crypto_skcipher_encrypt(req), &wait);
