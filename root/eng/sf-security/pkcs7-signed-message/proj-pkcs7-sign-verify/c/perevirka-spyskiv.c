/* Увімкнення перевірки CRL для всього ланцюга сертифікатів */
X509_STORE_set_flags(store, X509_V_FLAG_CRL_CHECK | X509_V_FLAG_CRL_CHECK_ALL);

/* Завантаження бінарного або PEM файлу CRL у довірене сховище */
BIO *crl_bio = BIO_new_file("revocations.crl", "r");
X509_CRL *crl = PEM_read_bio_X509_CRL(crl_bio, NULL, NULL, NULL);
if (crl) {
    X509_STORE_add_crl(store, crl);
    X509_CRL_free(crl);
}
BIO_free(crl_bio);
