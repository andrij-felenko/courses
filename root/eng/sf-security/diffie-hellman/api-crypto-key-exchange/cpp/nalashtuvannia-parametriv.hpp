auto pctx = std::unique_ptr<EVP_PKEY_CTX, decltype(&EVP_PKEY_CTX_free)>(
    EVP_PKEY_CTX_new_from_name(nullptr, "DH", nullptr), &EVP_PKEY_CTX_free);
EVP_PKEY_paramgen_init(pctx.get());

char group_name[] = "ffdhe3072";
std::array<OSSL_PARAM, 2> params = {
    OSSL_PARAM_construct_utf8_string("group", group_name, sizeof(group_name)),
    OSSL_PARAM_construct_end()
};

EVP_PKEY_CTX_set_params(pctx.get(), params.data());
EVP_PKEY *raw_params = nullptr;
EVP_PKEY_paramgen(pctx.get(), &raw_params);
auto dh_params = std::unique_ptr<EVP_PKEY, decltype(&EVP_PKEY_free)>(raw_params, &EVP_PKEY_free);
