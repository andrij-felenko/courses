struct crypto_skcipher *tfm = crypto_alloc_skcipher("xts(aes)", 0, 0);
u8 key[64];                                    /* два ключі AES-256 підряд */
u8 iv[16];                                     /* і його перепишуть */
u8 *buf = kmalloc(512, GFP_KERNEL);            /* вихід рівно такий, як вхід */

sg_init_one(&sg, buf, 512);
skcipher_request_set_callback(req, CRYPTO_TFM_REQ_MAY_BACKLOG |
                                   CRYPTO_TFM_REQ_MAY_SLEEP,
                             crypto_req_done, &wait);
skcipher_request_set_crypt(req, &sg, &sg, 512, iv);
err = crypto_wait_req(crypto_skcipher_encrypt(req), &wait);
