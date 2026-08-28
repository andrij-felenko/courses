// repo_verifier.cpp — Верифікатор підписів та хешів C++20 (RAII + std::expected + OpenSSL)
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <expected>
#include <filesystem>
#include <iomanip>
#include <sstream>
#include <gpgme.h>
#include <openssl/evp.h>

namespace fs = std::filesystem;

// RAII обгортки для автоматичного управління ресурсами GPGME
struct GpgmeCtxDeleter {
    void operator()(gpgme_ctx_t ctx) const {
        if (ctx) gpgme_release(ctx);
    }
};

struct GpgmeDataDeleter {
    void operator()(gpgme_data_t data) const {
        if (data) gpgme_data_release(data);
    }
};

using ScopedGpgCtx = std::unique_ptr<remove_pointer_t<gpgme_ctx_t>, GpgmeCtxDeleter>;
using ScopedGpgData = std::unique_ptr<remove_pointer_t<gpgme_data_t>, GpgmeDataDeleter>;

class RepositoryVerifier {
public:
    RepositoryVerifier() {
        gpgme_check_version(nullptr);
        gpgme_engine_check_version(GPGME_PROTOCOL_OpenPGP);
    }

    // Перевірка PGP-підпису індексного файлу
    [[nodiscard]] std::expected<std::string, std::string> verify_inrelease(
        const fs::path& keyring_path,
        const fs::path& inrelease_path) const 
    {
        gpgme_ctx_t raw_ctx = nullptr;
        if (auto err = gpgme_new(&raw_ctx); err != GPG_ERR_NO_ERROR) {
            return std::unexpected(std::string("Не вдалося створити контекст GPGME: ") + gpgme_strerror(err));
        }
        ScopedGpgCtx ctx(raw_ctx);

        if (auto err = gpgme_set_protocol(ctx.get(), GPGME_PROTOCOL_OpenPGP); err != GPG_ERR_NO_ERROR) {
            return std::unexpected(std::string("Помилка OpenPGP протоколу: ") + gpgme_strerror(err));
        }

        // Завантаження та імпорт відкритого ключа
        gpgme_data_t raw_key_data = nullptr;
        if (auto err = gpgme_data_new_from_file(&raw_key_data, keyring_path.string().c_str(), 1); err != GPG_ERR_NO_ERROR) {
            return std::unexpected(std::string("Не вдалося відкрити файл ключа: ") + gpgme_strerror(err));
        }
        ScopedGpgData key_data(raw_key_data);

        if (auto err = gpgme_op_import(ctx.get(), key_data.get()); err != GPG_ERR_NO_ERROR) {
            return std::unexpected(std::string("Помилка імпорту ключа: ") + gpgme_strerror(err));
        }

        // Зчитати та перевірити підпис InRelease
        gpgme_data_t raw_sig_data = nullptr;
        if (auto err = gpgme_data_new_from_file(&raw_sig_data, inrelease_path.string().c_str(), 1); err != GPG_ERR_NO_ERROR) {
            return std::unexpected(std::string("Не вдалося відкрити InRelease: ") + gpgme_strerror(err));
        }
        ScopedGpgData sig_data(raw_sig_data);

        if (auto err = gpgme_op_verify(ctx.get(), sig_data.get(), nullptr, nullptr); err != GPG_ERR_NO_ERROR) {
            return std::unexpected(std::string("Помилка під час верифікації: ") + gpgme_strerror(err));
        }

        auto* result = gpgme_op_verify_result(ctx.get());
        if (!result || !result->signatures) {
            return std::unexpected("Підпис відсутній у файлі метаданих.");
        }

        if (result->signatures->status != GPG_ERR_NO_ERROR) {
            return std::unexpected("Криптографічний підпис не дійсний!");
        }

        return std::string(result->signatures->fpr ? result->signatures->fpr : "UNKNOWN_FPR");
    }

    // Обчислення SHA-256 хешу файлу за допомогою RAII OpenSSL Context
    [[nodiscard]] static std::expected<std::string, std::string> calculate_sha256(const fs::path& file_path) {
        std::ifstream file(file_path, std::ios::binary);
        if (!file.is_open()) {
            return std::unexpected("Не вдалося відкрити файл для читання SHA-256");
        }

        std::unique_ptr<EVP_MD_CTX, void(*)(EVP_MD_CTX*)> mdctx(EVP_MD_CTX_new(), EVP_MD_CTX_free);
        if (!mdctx || 1 != EVP_DigestInit_ex(mdctx.get(), EVP_sha256(), nullptr)) {
            return std::unexpected("Помилка ініціалізації контексту OpenSSL SHA-256");
        }

        std::vector<char> buffer(8192);
        while (file.read(buffer.data(), buffer.size()) || file.gcount() > 0) {
            if (1 != EVP_DigestUpdate(mdctx.get(), buffer.data(), file.gcount())) {
                return std::unexpected("Помилка оновлення хешу SHA-256");
            }
        }

        unsigned char digest[EVP_MAX_MD_SIZE];
        unsigned int digest_len = 0;
        if (1 != EVP_DigestFinal_ex(mdctx.get(), digest, &digest_len)) {
            return std::unexpected("Помилка фіналізації SHA-256");
        }

        std::ostringstream ss;
        for (unsigned int i = 0; i < digest_len; ++i) {
            ss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(digest[i]);
        }
        return ss.str();
    }
};

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Використання: " << argv[0] << " <keyring.gpg> <InRelease> <target.deb>\n";
        return EXIT_FAILURE;
    }

    const fs::path keyring_path = argv[1];
    const fs::path inrelease_path = argv[2];
    const fs::path target_pkg_path = argv[3];

    RepositoryVerifier verifier;

    // 1. Верифікація GPG підпису
    auto fpr_result = verifier.verify_inrelease(keyring_path, inrelease_path);
    if (!fpr_result) {
        std::cerr << "[ПОМИЛКА] " << fpr_result.error() << "\n";
        return EXIT_FAILURE;
    }
    std::cout << "[ОК] GPG підпис валідний. Fingerprint: " << *fpr_result << "\n";

    // 2. Обчислення SHA-256 хешу
    auto sha_result = RepositoryVerifier::calculate_sha256(target_pkg_path);
    if (!sha_result) {
        std::cerr << "[ПОМИЛКА] " << sha_result.error() << "\n";
        return EXIT_FAILURE;
    }
    std::cout << "[ОК] Хеш пакунка " << target_pkg_path.filename() << ": " << *sha_result << "\n";

    return EXIT_SUCCESS;
}
