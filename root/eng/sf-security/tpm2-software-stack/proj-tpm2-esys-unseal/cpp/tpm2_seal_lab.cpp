// tpm2_seal_lab.cpp — Ідіоматична реалізація C++20 з використанням RAII та шаблонів
#include <iostream>
#include <algorithm>
#include <memory>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <stdexcept>
#include <format>
#include <tss2/tss2_esys.h>
#include <tss2/tss2_tctildr.h>

namespace tpm2 {

// RAII обгортки для автоматичного очищення контекстів TCTI та ESAPI
struct TctiDeleter {
    void operator()(TSS2_TCTI_CONTEXT* ctx) const noexcept {
        if (ctx) Tss2_TctiLdr_Finalize(&ctx);
    }
};
using TctiContextPtr = std::unique_ptr<TSS2_TCTI_CONTEXT, TctiDeleter>;

struct EsysDeleter {
    void operator()(ESYS_CONTEXT* ctx) const noexcept {
        if (ctx) Esys_Finalize(&ctx);
    }
};
using EsysContextPtr = std::unique_ptr<ESYS_CONTEXT, EsysDeleter>;

// RAII обгортка для тимчасових handles об'єктів TPM
class ScopedEsysHandle {
public:
    ScopedEsysHandle(ESYS_CONTEXT* esysCtx, ESYS_TR handle = ESYS_TR_NONE) noexcept
        : m_ctx(esysCtx), m_handle(handle) {}

    ~ScopedEsysHandle() {
        if (m_ctx && m_handle != ESYS_TR_NONE) {
            Esys_FlushContext(m_ctx, m_handle);
        }
    }

    ScopedEsysHandle(const ScopedEsysHandle&) = delete;
    ScopedEsysHandle& operator=(const ScopedEsysHandle&) = delete;

    ScopedEsysHandle(ScopedEsysHandle&& other) noexcept
        : m_ctx(other.m_ctx), m_handle(other.m_handle) {
        other.m_handle = ESYS_TR_NONE;
    }

    [[nodiscard]] ESYS_TR get() const noexcept { return m_handle; }
    [[nodiscard]] ESYS_TR* ptr() noexcept { return &m_handle; }

private:
    ESYS_CONTEXT* m_ctx{nullptr};
    ESYS_TR m_handle{ESYS_TR_NONE};
};

class Tpm2Session {
public:
    explicit Tpm2Session(const std::string& tctiName = "device:/dev/tpmrm0") {
        TSS2_TCTI_CONTEXT* tctiRaw = nullptr;
        TSS2_RC rc = Tss2_TctiLdr_Initialize(tctiName.c_str(), &tctiRaw);
        if (rc != TSS2_RC_SUCCESS) {
            throw std::runtime_error(std::format("Не вдалося відкрити TCTI: 0x{:08x}", rc));
        }
        m_tcti.reset(tctiRaw);

        ESYS_CONTEXT* esysRaw = nullptr;
        rc = Esys_Initialize(&esysRaw, m_tcti.get(), nullptr);
        if (rc != TSS2_RC_SUCCESS) {
            throw std::runtime_error(std::format("Помилка Esys_Initialize: 0x{:08x}", rc));
        }
        m_esys.reset(esysRaw);
    }

    [[nodiscard]] ESYS_CONTEXT* getContext() const noexcept { return m_esys.get(); }

    std::vector<uint8_t> sealAndUnseal(std::span<const uint8_t> secretData) {
        ESYS_CONTEXT* ctx = m_esys.get();

        // 1. Створення Primary Key
        ScopedEsysHandle primaryKey(ctx);
        TPM2B_PUBLIC primaryTemplate{
            .size = 0,
            .publicArea = {
                .type = TPM2_ALG_RSA,
                .nameAlg = TPM2_ALG_SHA256,
                .objectAttributes = (TPMA_OBJECT_USERWITHAUTH | TPMA_OBJECT_RESTRICTED |
                                     TPMA_OBJECT_DECRYPT | TPMA_OBJECT_FIXEDTPM | TPMA_OBJECT_FIXEDPARENT),
                .parameters = { .rsaDetail = {
                    .symmetric = { .algorithm = TPM2_ALG_AES, .keyBits = { .aes = 128 }, .mode = { .aes = TPM2_ALG_CFB } },
                    .scheme = { .scheme = TPM2_ALG_NULL },
                    .keyBits = 2048, .exponent = 0
                }}
            }
        };

        TSS2_RC rc = Esys_CreatePrimary(ctx, ESYS_TR_RH_OWNER, ESYS_TR_PASSWORD, ESYS_TR_NONE, ESYS_TR_NONE,
                                        &primaryTemplate, nullptr, nullptr, primaryKey.ptr(), nullptr, nullptr, nullptr, nullptr);
        if (rc != TSS2_RC_SUCCESS) {
            throw std::runtime_error(std::format("Esys_CreatePrimary помилка: 0x{:08x}", rc));
        }

        // 2. Ініціалізація сесії політики PCR
        ScopedEsysHandle policySession(ctx);
        TPMT_SYM_DEF symDef{ .algorithm = TPM2_ALG_NULL };
        rc = Esys_StartAuthSession(ctx, ESYS_TR_NONE, ESYS_TR_NONE, ESYS_TR_NONE, ESYS_TR_NONE, ESYS_TR_NONE,
                                   nullptr, TPM2_SE_POLICY, &symDef, TPM2_ALG_SHA256, policySession.ptr());
        if (rc != TSS2_RC_SUCCESS) {
            throw std::runtime_error(std::format("Esys_StartAuthSession помилка: 0x{:08x}", rc));
        }

        TPML_PCR_SELECTION pcrSel{
            .count = 1,
            .pcrSelections = { {{ .hash = TPM2_ALG_SHA256, .sizeofSelect = 3, .pcrSelect = { 0x81, 0x00, 0x00 } }} }
        };
        rc = Esys_PolicyPCR(ctx, policySession.get(), ESYS_TR_NONE, ESYS_TR_NONE, ESYS_TR_NONE, nullptr, &pcrSel);
        if (rc != TSS2_RC_SUCCESS) {
            throw std::runtime_error(std::format("Esys_PolicyPCR помилка: 0x{:08x}", rc));
        }

        TPM2B_DIGEST* policyDigestRaw = nullptr;
        rc = Esys_PolicyGetDigest(ctx, policySession.get(), ESYS_TR_NONE, ESYS_TR_NONE, ESYS_TR_NONE, &policyDigestRaw);
        if (rc != TSS2_RC_SUCCESS) {
            throw std::runtime_error(std::format("Esys_PolicyGetDigest помилка: 0x{:08x}", rc));
        }
        std::unique_ptr<TPM2B_DIGEST, decltype([](auto* p){ Esys_Free(p); })> policyDigest(policyDigestRaw);

        // 3. Запечатування секрету
        TPM2B_SENSITIVE_CREATE sensitiveData{};
        if (secretData.size() > sizeof(sensitiveData.sensitive.data.buffer)) {
            throw std::runtime_error("Секрет не вміщається у TPM2B_SENSITIVE_DATA");
        }
        sensitiveData.sensitive.data.size = static_cast<UINT16>(secretData.size());
        std::copy(secretData.begin(), secretData.end(), sensitiveData.sensitive.data.buffer);

        TPM2B_PUBLIC sealTemplate{
            .size = 0,
            .publicArea = {
                .type = TPM2_ALG_KEYEDHASH,
                .nameAlg = TPM2_ALG_SHA256,
                .objectAttributes = (TPMA_OBJECT_FIXEDTPM | TPMA_OBJECT_FIXEDPARENT),
                .parameters = { .keyedHashDetail = { .scheme = { .scheme = TPM2_ALG_NULL } } }
            }
        };

        sealTemplate.publicArea.authPolicy = *policyDigest;

        TPM2B_PRIVATE* outPrivateRaw = nullptr;
        TPM2B_PUBLIC* outPublicRaw = nullptr;
        rc = Esys_Create(ctx, primaryKey.get(), ESYS_TR_PASSWORD, ESYS_TR_NONE, ESYS_TR_NONE,
                         &sensitiveData, &sealTemplate, nullptr, nullptr, &outPrivateRaw, &outPublicRaw, nullptr, nullptr, nullptr);
        if (rc != TSS2_RC_SUCCESS) {
            throw std::runtime_error(std::format("Esys_Create seal помилка: 0x{:08x}", rc));
        }

        std::unique_ptr<TPM2B_PRIVATE, decltype([](auto* p){ Esys_Free(p); })> outPriv(outPrivateRaw);
        std::unique_ptr<TPM2B_PUBLIC, decltype([](auto* p){ Esys_Free(p); })> outPub(outPublicRaw);

        // 4. Завантаження та Unseal
        ScopedEsysHandle loadedObject(ctx);
        rc = Esys_Load(ctx, primaryKey.get(), ESYS_TR_PASSWORD, ESYS_TR_NONE, ESYS_TR_NONE,
                       outPriv.get(), outPub.get(), loadedObject.ptr());
        if (rc != TSS2_RC_SUCCESS) {
            throw std::runtime_error(std::format("Esys_Load помилка: 0x{:08x}", rc));
        }

        TPM2B_SENSITIVE_DATA* unsealedRaw = nullptr;
        rc = Esys_Unseal(ctx, loadedObject.get(), policySession.get(), ESYS_TR_NONE, ESYS_TR_NONE, &unsealedRaw);
        if (rc != TSS2_RC_SUCCESS) {
            throw std::runtime_error(std::format("Esys_Unseal помилка: 0x{:08x}", rc));
        }

        std::unique_ptr<TPM2B_SENSITIVE_DATA, decltype([](auto* p){ Esys_Free(p); })> unsealedPtr(unsealedRaw);
        return {unsealedPtr->buffer, unsealedPtr->buffer + unsealedPtr->size};
    }

private:
    TctiContextPtr m_tcti;
    EsysContextPtr m_esys;
};

} // namespace tpm2

int main() {
    try {
        tpm2::Tpm2Session session("device:/dev/tpmrm0");
        std::string secretText = "Cxx20-Secure-LUKS-MasterKey";
        std::span<const uint8_t> payload(reinterpret_cast<const uint8_t*>(secretText.data()), secretText.size() + 1);

        std::cout << "[+] Виконання Sealing & Unsealing через C++ RAII...\n";
        auto result = session.sealAndUnseal(payload);

        std::cout << "[УСПІХ] Розпечатаний секрет: \"" << reinterpret_cast<const char*>(result.data()) << "\"\n";
    } catch (const std::exception& ex) {
        std::cerr << "[КРИТИЧНА ПОМИЛКА] " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
