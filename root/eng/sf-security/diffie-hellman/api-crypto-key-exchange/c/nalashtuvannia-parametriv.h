EVP_PKEY_CTX *pctx = EVP_PKEY_CTX_new_from_name(NULL, "DH", NULL);
EVP_PKEY_paramgen_init(pctx);

char group_name[] = "ffdhe3072";
OSSL_PARAM params[2];
params[0] = OSSL_PARAM_construct_utf8_string("group", group_name, sizeof(group_name));
params[1] = OSSL_PARAM_construct_end();

EVP_PKEY_CTX_set_params(pctx, params);
EVP_PKEY *dh_params = NULL;
EVP_PKEY_paramgen(pctx, &dh_params);
EVP_PKEY_CTX_free(pctx);
