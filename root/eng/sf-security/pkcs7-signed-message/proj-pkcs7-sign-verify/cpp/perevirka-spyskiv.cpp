// Увімкнення суворої перевірки CRL у C++23
X509_STORE_set_flags(store.get(), X509_V_FLAG_CRL_CHECK | X509_V_FLAG_CRL_CHECK_ALL);

SslPtr<BIO> crl_bio{BIO_new_file("revocations.crl", "r")};
if (crl_bio) {
    SslPtr<X509_CRL> crl{PEM_read_bio_X509_CRL(crl_bio.get(), nullptr, nullptr, nullptr)};
    if (crl) {
        X509_STORE_add_crl(store.get(), crl.get());
    }
}
