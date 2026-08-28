#include <iostream>
#include <fstream>
#include <vector>
#include <span>
#include <string>
#include <string_view>
#include <sstream>
#include <iomanip>
#include <memory>
#include <expected>
#include <openssl/evp.h>
#include <openssl/sha.h>
#include <openssl/pem.h>

// Структура розібраної атестації SLSA v1.0
struct SlsaProvenance {
    std::string subject_name;
    std::string subject_sha256;
    std::string builder_id;
    std::string source_uri;
    std::string source_commit;
};

// RAII обгортки для коректного звільнення ресурсів OpenSSL
struct EvpMdCtxDeleter {
    void operator()(EVP_MD_CTX* ctx) const { if (ctx) EVP_MD_CTX_free(ctx); }
};
using ScopedMdCtx = std::unique_ptr<EVP_MD_CTX, EvpMdCtxDeleter>;

struct EvpPkeyDeleter {
    void operator()(EVP_PKEY* pkey) const { if (pkey) EVP_PKEY_free(pkey); }
};
using ScopedPkey = std::unique_ptr<EVP_PKEY, EvpPkeyDeleter>;

// 1. Потокове обчислення SHA-256 гешу файлу на диску
std::expected<std::string, std::string> calculate_sha256(std::string_view filepath) {
    std::ifstream file(std::string(filepath), std::ios::binary);
    if (!file.is_open()) {
        return std::unexpected("Неможливо відкрити цільовий файл артефакту");
    }

    ScopedMdCtx ctx(EVP_MD_CTX_new());
    if (!ctx || EVP_DigestInit_ex(ctx.get(), EVP_sha256(), nullptr) != 1) {
        return std::unexpected("Помилка ініціалізації контексту EVP_MD");
    }

    std::vector<char> buffer(65536);
    while (file.read(buffer.data(), buffer.size()) || file.gcount() > 0) {
        if (EVP_DigestUpdate(ctx.get(), buffer.data(), file.gcount()) != 1) {
            return std::unexpected("Помилка обчислення проміжного гешу");
        }
    }

    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int length = 0;
    if (EVP_DigestFinal_ex(ctx.get(), hash, &length) != 1) {
        return std::unexpected("Помилка фіналізації гешу");
    }

    std::ostringstream ss;
    for (unsigned int i = 0; i < length; ++i) {
        ss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(hash[i]);
    }
    return ss.str();
}

// 2. Декодування Base64 рядка
std::expected<std::string, std::string> base64_decode(std::string_view input) {
    std::vector<unsigned char> output(input.size());
    int len = EVP_DecodeBlock(output.data(), 
                              reinterpret_cast<const unsigned char*>(input.data()), 
                              static_cast<int>(input.size()));
    if (len < 0) {
        return std::unexpected("Помилка декодування Base64 корисного навантаження");
    }
    
    // Коригування padding символів '='
    int pad = 0;
    if (input.ends_with("==")) pad = 2;
    else if (input.ends_with("=")) pad = 1;

    return std::string(reinterpret_cast<char*>(output.data()), len - pad);
}

// 3. Перевірка цифрового підпису ECDSA над payload
bool verify_ecdsa_signature(std::string_view payload, 
                            std::string_view signature_b64, 
                            std::string_view public_key_pem) {
    auto sig_raw = base64_decode(signature_b64);
    if (!sig_raw) return false;

    BIO* bio = BIO_new_mem_buf(public_key_pem.data(), static_cast<int>(public_key_pem.size()));
    if (!bio) return false;

    ScopedPkey pkey(PEM_read_bio_PUBKEY(bio, nullptr, nullptr, nullptr));
    BIO_free(bio);
    if (!pkey) return false;

    ScopedMdCtx ctx(EVP_MD_CTX_new());
    if (!ctx) return false;

    if (EVP_DigestVerifyInit(ctx.get(), nullptr, EVP_sha256(), nullptr, pkey.get()) != 1) {
        return false;
    }

    if (EVP_DigestVerifyUpdate(ctx.get(), payload.data(), payload.size()) != 1) {
        return false;
    }

    int rc = EVP_DigestVerifyFinal(ctx.get(), 
                                   reinterpret_cast<const unsigned char*>(sig_raw->data()), 
                                   sig_raw->size());
    return rc == 1;
}

// 4. Політика оцінки відповідності параметрів збирання
bool evaluate_policy(const SlsaProvenance& prov, 
                     std::string_view expected_builder, 
                     std::string_view expected_repo) {
    if (prov.builder_id != expected_builder) {
        std::cerr << "[ВІДМОВА] Недовірений Builder ID: " << prov.builder_id 
                  << " (очікувався: " << expected_builder << ")\n";
        return false;
    }
    if (prov.source_uri != expected_repo) {
        std::cerr << "[ВІДМОВА] Невідповідність репозиторію джерела: " << prov.source_uri 
                  << " (очікувався: " << expected_repo << ")\n";
        return false;
    }
    return true;
}

// Головна процедура аудиту артефакту
int verify_artifact(std::string_view artifact_path, 
                    const SlsaProvenance& prov, 
                    std::string_view payload_json, 
                    std::string_view signature_b64, 
                    std::string_view public_key_pem) {
    std::cout << "[1/4] Обчислення контрольного гешу артефакту: " << artifact_path << "...\n";
    auto digest = calculate_sha256(artifact_path);
    if (!digest) {
        std::cerr << "[ПОМИЛКА] " << digest.error() << "\n";
        return 1;
    }
    std::cout << "      Отримано SHA-256: " << *digest << "\n";

    std::cout << "[2/4] Звірка дайджесту з суб'єктом атестації...\n";
    if (*digest != prov.subject_sha256) {
        std::cerr << "[ВІДХИЛЕНО] Геш артефакту (" << *digest 
                  << ") не збігається з атестацією (" << prov.subject_sha256 << ")!\n";
        return 2;
    }
    std::cout << "      Геші збігаються. Цілісність файлу підтверджена.\n";

    std::cout << "[3/4] Перевірка цифрового підпису атестації...\n";
    if (!verify_ecdsa_signature(payload_json, signature_b64, public_key_pem)) {
        std::cerr << "[ВІДХИЛЕНО] Недійсний цифровий підпис атестації!\n";
        return 3;
    }
    std::cout << "      Криптографічний підпис дійсний.\n";

    std::cout << "[4/4] Оцінка правил політики SLSA L3...\n";
    if (!evaluate_policy(prov, 
                         "https://github.com/actions/runner/slsa-builder-generic@v2", 
                         "git+https://github.com/enterprise/payment-gateway")) {
        std::cerr << "[ВІДХИЛЕНО] Порушення правил безпеки походження!\n";
        return 4;
    }

    std::cout << "[УСПІХ] Артефакт повністю верифіковано. Допущено до виконання.\n";
    return 0;
}
