/* skcipher */
req = skcipher_request_alloc(tfm, GFP_KERNEL);
skcipher_request_set_callback(req, flags, compl, data);
skcipher_request_set_crypt(req, src_sg, dst_sg, cryptlen, iv);
err = crypto_skcipher_encrypt(req);          /* або crypto_skcipher_decrypt */

/* ahash: або одним махом, або init → update… → final */
ahash_request_set_crypt(req, src_sg, result, nbytes);
err = crypto_ahash_digest(req);              /* finup = update + final */

/* aead: асоційовані дані й корисне навантаження — в одному списку */
aead_request_set_ad(req, assoclen);
aead_request_set_crypt(req, src_sg, dst_sg, cryptlen, iv);
err = crypto_aead_encrypt(req);

/* akcipher */
akcipher_request_set_crypt(req, src_sg, dst_sg, src_len, dst_len);
err = crypto_akcipher_encrypt(req);

/* kpp: вхід і вихід задають окремо */
kpp_request_set_input(req, in_sg, in_len);
kpp_request_set_output(req, out_sg, out_len);
err = crypto_kpp_generate_public_key(req);   /* потім _compute_shared_secret */

/* acomp */
acomp_request_set_params(req, src_sg, dst_sg, slen, dlen);
err = crypto_acomp_compress(req);            /* або crypto_acomp_decompress */
