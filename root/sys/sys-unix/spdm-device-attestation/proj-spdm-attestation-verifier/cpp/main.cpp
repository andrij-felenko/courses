#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <span>
#include <expected>
#include <filesystem>

#include <openssl/bio.h>
#include <openssl/x509.h>
#include <openssl/evp.h>

namespace fs = std::filesystem;

// RAII обгортки для гарантованого звільнення криптографічних ресурсів OpenSSL
struct X509Deleter {
    void operator()(X509* cert) const noexcept {
        if (cert) X509_free(cert);
    }
};

struct EvpMdCtxDeleter {
    void operator()(EVP_MD_CTX* ctx) const noexcept {
        if (ctx) EVP_MD_CTX_free(ctx);
    }
};

using X509Ptr = std::unique_ptr<X509, X509Deleter>;
using EvpMdCtxPtr = std::unique_ptr<EVP_MD_CTX, EvpMdCtxDeleter>;

// Системні коди помилок атестації
enum class AttestationError {
    FileNotFound,
    ReadFailed,
    ParseCertificateFailed,
    ExtractKeyFailed,
    VerifyInitFailed,
    InvalidSignatureLength,
    SignatureVerificationFailed
};

class SpdmAttestationVerifier {
public:
    explicit SpdmAttestationVerifier(fs::path sysfs_dir)
        : sysfs_dir_(std::move(sysfs_dir)) {}

    [[nodiscard]] std::expected<void, AttestationError> verify() const {
        auto cert_data_res = read_file(sysfs_dir_ / "certificates" / "slot0");
        if (!cert_data_res) return std::unexpected(cert_data_res.error());

        auto meas_data_res = read_file(sysfs_dir_ / "measurements" / "raw");
        if (!meas_data_res) return std::unexpected(meas_data_res.error());

        const auto& cert_bytes = *cert_data_res;
        const auto& meas_bytes = *meas_data_res;

        const unsigned char* p = cert_bytes.data();
        X509Ptr cert{d2i_X509(nullptr, &p, static_cast<long>(cert_bytes.size()))};
        if (!cert) {
            return std::unexpected(AttestationError::ParseCertificateFailed);
        }

        EVP_PKEY* pubkey = X509_get0_pubkey(cert.get());
        if (!pubkey) {
            return std::unexpected(AttestationError::ExtractKeyFailed);
        }

        EvpMdCtxPtr ctx{EVP_MD_CTX_new()};
        if (!ctx) {
            return std::unexpected(AttestationError::VerifyInitFailed);
        }

        if (EVP_DigestVerifyInit(ctx.get(), nullptr, EVP_sha384(), nullptr, pubkey) <= 0) {
            return std::unexpected(AttestationError::VerifyInitFailed);
        }

        constexpr size_t sig_len = 96; // Довжина підпису ECDSA-P384
        if (meas_bytes.size() <= sig_len) {
            return std::unexpected(AttestationError::InvalidSignatureLength);
        }

        size_t data_len = meas_bytes.size() - sig_len;
        std::span<const unsigned char> payload_span{meas_bytes.data(), data_len};
        std::span<const unsigned char> sig_span{meas_bytes.data() + data_len, sig_len};

        if (EVP_DigestVerifyUpdate(ctx.get(), payload_span.data(), payload_span.size()) <= 0) {
            return std::unexpected(AttestationError::SignatureVerificationFailed);
        }

        int rc = EVP_DigestVerifyFinal(ctx.get(), sig_span.data(), sig_span.size());
        if (rc == 1) {
            return {}; // Успішна верифікація підпису
        }

        return std::unexpected(AttestationError::SignatureVerificationFailed);
    }

private:
    fs::path sysfs_dir_;

    [[nodiscard]] static std::expected<std::vector<unsigned char>, AttestationError> 
    read_file(const fs::path& path) {
        std::ifstream file(path, std::ios::binary);
        if (!file.is_open()) {
            return std::unexpected(AttestationError::FileNotFound);
        }

        std::vector<unsigned char> buffer(
            (std::istreambuf_iterator<char>(file)),
            std::istreambuf_iterator<char>()
        );

        if (buffer.empty()) {
            return std::unexpected(AttestationError::ReadFailed);
        }

        return buffer;
    }
};

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <sysfs_spdm_path>\n";
        return 1;
    }

    SpdmAttestationVerifier verifier{argv[1]};
    auto result = verifier.verify();

    if (result.has_value()) {
        std::cout << "SUCCESS: SPDM measurement signature is VALID for " << argv[1] << "\n";
        return 0;
    }

    std::cerr << "FAILURE: SPDM attestation failed with error code: " 
              << static_cast<int>(result.error()) << "\n";
    return 1;
}
