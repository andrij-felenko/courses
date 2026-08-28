#include <iostream>
#include <string_view>
#include <openssl/x509_vfy.h>

int custom_verify_callback(int preverify_ok, X509_STORE_CTX *x509_ctx) noexcept {
    if (!preverify_ok) {
        const int err = X509_STORE_CTX_get_error(x509_ctx);
        const int depth = X509_STORE_CTX_get_error_depth(x509_ctx);
        const std::string_view err_str = X509_verify_cert_error_string(err);
        std::cerr << "[!] Помилка валідації на глибині " << depth << ": " << err_str << "\n";
    }
    return preverify_ok;
}
