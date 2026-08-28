SHASH_DESC_ON_STACK(desc, tfm);
desc->tfm = tfm;
crypto_shash_init(desc);
crypto_shash_update(desc, data, len);
crypto_shash_final(desc, out);
crypto_shash_tfm_digest(tfm, data, len, out);      /* те саме одним викликом */

crypto_lskcipher_encrypt(tfm, src, dst, len, siv); /* суцільні буфери, siv — вектор */
crypto_cipher_encrypt_one(tfm, dst, src);          /* рівно blocksize байтів */

crypto_sig_sign(tfm, src, slen, dst, dlen);
crypto_sig_verify(tfm, src, slen, digest, dlen);   /* ненуль = підпис не збігся */
crypto_rng_get_bytes(tfm, out, len);
